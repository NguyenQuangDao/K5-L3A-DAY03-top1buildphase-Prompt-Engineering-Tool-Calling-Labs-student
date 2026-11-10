from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import ResearchAgent  # noqa: E402
from env_loader import load_lab_env  # noqa: E402
from providers import make_provider  # noqa: E402
from providers.base import ModelResponse, ToolCall  # noqa: E402
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools  # noqa: E402
from ui_components import (  # noqa: E402
    render_clarify_options,
    render_confirmation_card,
    render_tool_inspector,
    render_welcome_screen,
)
from ui_components.theme import build_shadcn_css  # noqa: E402
from versioning import ArtifactVersion, artifact_version_dict, build_artifact_version  # noqa: E402

ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_YAML_PATH = ARTIFACTS_DIR / "tools.yaml"

load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent — AI Workspace",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================================
# HELPER UTILITIES & SAFE PROVIDER ADAPTER
# =====================================================================
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "session"


def json_text(value: Any, *, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def trim_history(history: list[dict[str, str]], window: int) -> list[dict[str, str]]:
    if window <= 0:
        return []
    return history[-window * 2 :]


class UIProviderAdapter:
    """Thin UI adapter around backend Provider.

    Preserves 100% of the backend Provider protocol while handling OpenRouter's
    credit-reservation limit (HTTP 402 when default max_tokens=16384 exceeds remaining
    account credits) by retrying with a bounded max_tokens=1024 on the underlying client.
    Never fabricates responses or tool calls.
    """

    def __init__(self, provider_name: str, base_provider: Any, max_tokens: int = 1024) -> None:
        self.provider_name = provider_name
        self.base_provider = base_provider
        self.max_tokens = max_tokens
        self.default_model = getattr(base_provider, "default_model", None)

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            return self.base_provider.complete(
                messages,
                tools,
                model=model,
                temperature=temperature,
                tool_choice=tool_choice,
            )
        except Exception as exc:
            err_text = str(exc)
            if self.provider_name in {"openrouter", "openai"} and "402" in err_text and "max_tokens" in err_text:
                return self._complete_with_bounded_tokens(
                    messages,
                    tools,
                    model=model,
                    temperature=temperature,
                    tool_choice=tool_choice,
                )
            if self.provider_name == "openrouter" and "429" in err_text:
                return self._complete_with_bounded_tokens(
                    messages,
                    tools,
                    model="cohere/command-r7b-12-2024",
                    temperature=temperature,
                    tool_choice=tool_choice,
                )
            raise

    def _complete_with_bounded_tokens(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        from openai import OpenAI

        api_key = os.getenv(self.base_provider.api_key_env) or getattr(self.base_provider, "api_key_default", None)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.base_provider.api_key_env}")

        client = OpenAI(api_key=api_key, base_url=self.base_provider.base_url)
        kwargs: dict[str, Any] = {
            "model": model or self.base_provider.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        resp = client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            raw_args = call.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {"_invalid_json_arguments": raw_args}
            if not isinstance(args, dict):
                args = {"_invalid_json_arguments": raw_args}
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)


def check_provider_status(provider_name: str) -> tuple[str, str]:
    """Return ('ok' | 'warn' | 'err', human_readable_status) without leaking any secret."""
    env_map = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    if provider_name == "ollama":
        import requests

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").replace("/v1", "")
        try:
            resp = requests.get(f"{base_url}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                models = [m.get("name", "") for m in resp.json().get("models", [])]
                return ("ok", f"Đã kết nối ({len(models)} local)")
            return ("warn", f"HTTP {resp.status_code}")
        except Exception:
            return ("err", "Daemon offline")

    env_key = env_map.get(provider_name, "")
    val = os.getenv(env_key, "")
    if val:
        return ("ok", "Đã cấu hình API key")
    return ("err", f"Thiếu {env_key}")


def check_tool_env_readiness() -> list[tuple[str, str, str]]:
    """Return list of (service_name, dot_class, status_label) without exposing values."""
    return [
        ("arXiv API (papers / paper_text)", "ok", "Sẵn sàng"),
        ("Company Policy KB (policy)", "ok", "Sẵn sàng"),
        ("Digest Formatter (format)", "ok", "Sẵn sàng"),
        ("Clarification Guard (clarify)", "ok", "Sẵn sàng"),
        (
            "Tavily Search (lookup)",
            "ok" if os.getenv("TAVILY_API_KEY") else "warn",
            "Đã cấu hình" if os.getenv("TAVILY_API_KEY") else "Thiếu TAVILY_API_KEY",
        ),
        (
            "Firecrawl Scrape (fetch)",
            "ok" if os.getenv("FIRECRAWL_API_KEY") else "warn",
            "Đã cấu hình" if os.getenv("FIRECRAWL_API_KEY") else "Thiếu FIRECRAWL_API_KEY",
        ),
        (
            "RapidAPI Twitter (timeline / social)",
            "ok" if os.getenv("RAPIDAPI_KEY") else "warn",
            "Đã cấu hình" if os.getenv("RAPIDAPI_KEY") else "Thiếu RAPIDAPI_KEY",
        ),
        (
            "Telegram Bot (send)",
            "ok" if (os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID")) else "warn",
            "Đã cấu hình"
            if (os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))
            else "Thiếu biến môi trường TELEGRAM",
        ),
    ]


def classify_tool_event_status(event: dict[str, Any]) -> str:
    """Classify a tool event into one of the 5 standard Inspector statuses."""
    explicit = event.get("ui_status")
    if explicit in {"Pending", "Running", "Completed", "Failed", "Awaiting Confirmation"}:
        return explicit

    result = event.get("result", {})
    if not isinstance(result, dict):
        return "Completed"
    if result.get("status") == "needs_confirmation" or result.get("awaiting_user") is True:
        return "Awaiting Confirmation"
    if result.get("error"):
        return "Failed"
    return "Completed"


# =====================================================================
# AGENT EXECUTION & GUARDRAIL ENGINE (Reusing chat.py & agent.py contracts)
# =====================================================================
def execute_single_tool(call: ToolCall, *, allow_confirmed_send: bool = False) -> dict[str, Any]:
    """Execute a tool from TOOL_FUNCTIONS while enforcing the UI confirmation guardrail."""
    func = TOOL_FUNCTIONS.get(call.name)
    call_args = dict(call.args or {})

    if not func:
        event = {
            "tool": call.name,
            "args": call_args,
            "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
            "duration_ms": 0,
        }
        event["ui_status"] = classify_tool_event_status(event)
        return event

    # Safety Guardrail: Never pass confirmed=True to `send` without explicit UI approval.
    if call.name == "send" and not allow_confirmed_send:
        call_args["confirmed"] = False

    t0 = time.perf_counter()
    try:
        result = func(**call_args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    duration_ms = round((time.perf_counter() - t0) * 1000)

    event = {
        "tool": call.name,
        "args": call_args,
        "result": result,
        "duration_ms": duration_ms,
    }
    event["ui_status"] = classify_tool_event_status(event)
    return event


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    clean_events = [
        {"tool": e["tool"], "args": e["args"], "result": e["result"]}
        for e in events
    ]
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(clean_events, max_chars=24000)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    call_summary = [{"name": call.name, "args": call.args} for call in calls]
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(call_summary)}",
    }


def run_interactive_agent_turn(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
    max_tool_rounds: int,
    status_container: Any | None = None,
) -> dict[str, Any]:
    """Run the multi-round tool loop, pausing immediately on `clarify` or `send`."""
    working_messages = list(messages)
    rounds: list[dict[str, Any]] = []
    all_tool_events: list[dict[str, Any]] = []
    pending_confirmation: dict[str, Any] | None = None

    for round_index in range(1, max_tool_rounds + 1):
        if status_container is not None:
            status_container.update(
                label=f"Round {round_index}/{max_tool_rounds} · Planning next step ({model})...",
                state="running",
            )

        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record: dict[str, Any] = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "rounds": rounds,
                "tool_events": all_tool_events,
                "pending_confirmation": None,
            }

        working_messages.append(assistant_tool_message(response.text, calls))
        non_blocking_events: list[dict[str, Any]] = []

        for step_idx, call in enumerate(calls, start=1):
            if status_container is not None:
                status_container.update(
                    label=f"Round {round_index} · Running `{call.name}` ({step_idx}/{len(calls)})...",
                    state="running",
                )
            event = execute_single_tool(call, allow_confirmed_send=False)
            event["round"] = round_index
            event["step"] = len(all_tool_events) + 1
            round_record["tool_results"].append(
                {"tool": event["tool"], "args": event["args"], "result": event["result"]}
            )
            all_tool_events.append(event)

            result = event.get("result", {})
            if isinstance(result, dict) and result.get("status") == "needs_confirmation":
                planned_text = str(call.args.get("text") or "")
                pending_confirmation = {
                    "confirmation_id": f"confirm_{uuid.uuid4().hex[:10]}",
                    "tool_name": call.name,
                    "underlying_tool": result.get("tool", "send_telegram"),
                    "text": planned_text,
                    "destination": (
                        f"Telegram Chat ({os.getenv('TELEGRAM_CHAT_ID')})"
                        if os.getenv("TELEGRAM_CHAT_ID")
                        else "Telegram Channel (TELEGRAM_CHAT_ID)"
                    ),
                    "args": dict(call.args or {}),
                    "resolved": False,
                    "decision": None,
                }
                rounds.append(round_record)
                prompt_msg = (
                    f"Hành động `{call.name}` yêu cầu xác nhận trước khi gửi lên Telegram.\n\n"
                    f"Vui lòng kiểm tra nội dung và chọn **Approve & Send** hoặc **Reject** ở bên dưới."
                )
                return {
                    "status": "awaiting_confirmation",
                    "assistant_text": prompt_msg,
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                    "pending_confirmation": pending_confirmation,
                }

            if isinstance(result, dict) and result.get("awaiting_user"):
                question = (
                    result.get("question")
                    or call.args.get("question")
                    or "Bạn vui lòng bổ sung thêm thông tin để mình tiếp tục nhé."
                )
                rounds.append(round_record)
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                    "pending_confirmation": None,
                }

            non_blocking_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_blocking_events))

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Đã dừng sau {max_tool_rounds} vòng gọi tool. Xem chi tiết trong Tool Call Inspector.",
        "rounds": rounds,
        "tool_events": all_tool_events,
        "pending_confirmation": None,
    }


# =====================================================================
# TRANSCRIPT PERSISTENCE (Matches chat.py JSON schema 100%)
# =====================================================================
def build_session_transcript(
    *,
    session_id: str,
    version_label: str,
    provider_name: str,
    model_name: str,
    history_window: int,
    max_tool_rounds: int,
    created_at: str,
    turns: list[dict[str, Any]],
) -> dict[str, Any]:
    artifact_ver: ArtifactVersion = build_artifact_version(
        version_label, SYSTEM_PROMPT_PATH, TOOLS_YAML_PATH
    )
    clean_turns = []
    for t in turns:
        clean_events = [
            {"tool": e["tool"], "args": e["args"], "result": e["result"]}
            for e in t.get("tool_events", [])
        ]
        clean_turns.append({
            "turn_index": t["turn_index"],
            "started_at": t["started_at"],
            "user": t["user"],
            "status": t["status"],
            "assistant_text": t["assistant_text"],
            "rounds": t.get("rounds", []),
            "tool_events": clean_events,
            "ended_at": t.get("ended_at", now_iso()),
        })
    return {
        "transcript_id": session_id,
        **artifact_version_dict(artifact_ver),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": "artifacts/system_prompt.md",
        "tools": "artifacts/tools.yaml",
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": created_at,
        "updated_at": now_iso(),
        "turns": clean_turns,
    }


def save_session_transcript(transcript: dict[str, Any], custom_filename: str | None = None) -> Path:
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = custom_filename or f"{transcript['transcript_id']}.transcript.json"
    path = TRANSCRIPTS_DIR / filename
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


# =====================================================================
# SESSION STATE INITIALIZATION
# =====================================================================
def create_new_conversation(version_label: str = "v3", provider_name: str = "openrouter") -> dict[str, Any]:
    ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    session_id = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{ts}"
    return {
        "session_id": session_id,
        "title": "Phiên nghiên cứu mới",
        "created_at": now_iso(),
        "messages": [],
        "turns": [],
        "history_pairs": [],
        "last_saved_path": None,
    }


if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "conversations" not in st.session_state:
    initial_conv = create_new_conversation("v3", "openrouter")
    st.session_state.conversations = {initial_conv["session_id"]: initial_conv}
    st.session_state.active_session_id = initial_conv["session_id"]

if "executed_confirmations" not in st.session_state:
    st.session_state.executed_confirmations = set()

if "auto_opened_dialogs" not in st.session_state:
    st.session_state.auto_opened_dialogs = set()

if "handled_component_events" not in st.session_state:
    st.session_state.handled_component_events = set()

if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = None

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False


def get_active_conversation() -> dict[str, Any]:
    active_id = st.session_state.active_session_id
    if active_id not in st.session_state.conversations:
        conv = create_new_conversation()
        st.session_state.conversations[conv["session_id"]] = conv
        st.session_state.active_session_id = conv["session_id"]
    conv = st.session_state.conversations[st.session_state.active_session_id]
    # Keep st.session_state.messages synchronized with active conversation
    st.session_state.messages = conv["messages"]
    return conv


# Apply active shadcn/ui theme CSS
st.markdown(build_shadcn_css(st.session_state.theme), unsafe_allow_html=True)


# =====================================================================
# SIDEBAR LAYOUT (Minimalist Navigation, Sessions & Provider Config)
# =====================================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sb-brand">
            <div>
                <div class="sb-brand-name">Trợ lý Nghiên cứu</div>
                <div style="font-size: 0.74rem; color: var(--muted-fg);">Không gian Nghiên cứu AI</div>
            </div>
            <span class="ws-pill"><strong>v3</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋ Đoạn chat mới", type="primary", use_container_width=True):
        prev_provider = st.session_state.get("sidebar_provider", "openrouter")
        prev_version = st.session_state.get("sidebar_version", "v3")
        new_c = create_new_conversation(prev_version, prev_provider)
        st.session_state.conversations[new_c["session_id"]] = new_c
        st.session_state.active_session_id = new_c["session_id"]
        st.rerun()

    st.markdown('<div class="sb-section-label">Lịch sử hội thoại</div>', unsafe_allow_html=True)
    search_query = st.text_input(
        "Tìm kiếm phiên",
        placeholder="Tìm kiếm cuộc trò chuyện...",
        label_visibility="collapsed",
        key="session_search",
    ).strip().lower()

    conv_ids = list(reversed(list(st.session_state.conversations.keys())))
    filtered_ids = [
        cid
        for cid in conv_ids
        if not search_query
        or search_query in st.session_state.conversations[cid]["title"].lower()
    ]

    if filtered_ids:
        for cid in filtered_ids[:12]:
            conv_item = st.session_state.conversations[cid]
            is_active = cid == st.session_state.active_session_id
            turns_count = len(conv_item["turns"])
            label_prefix = "● " if is_active else ""
            btn_label = f"{label_prefix}{conv_item['title']} ({turns_count})"
            if st.button(
                btn_label,
                key=f"nav_conv_{cid}",
                use_container_width=True,
            ):
                if not is_active:
                    st.session_state.active_session_id = cid
                    st.rerun()
    else:
        st.caption("Không tìm thấy cuộc trò chuyện phù hợp.")

    if TRANSCRIPTS_DIR.exists():
        saved_files = sorted(TRANSCRIPTS_DIR.glob("*.json"), reverse=True)
        if saved_files:
            with st.expander(f"Nhật ký đã lưu ({len(saved_files)})", expanded=False):
                for fpath in saved_files[:15]:
                    st.caption(f"`{fpath.name}`")

    st.divider()
    st.markdown('<div class="sb-section-label">Không gian làm việc & Mô hình</div>', unsafe_allow_html=True)

    provider_options = ["openrouter", "ollama", "gemini", "openai", "anthropic"]
    selected_provider = st.selectbox(
        "Nhà cung cấp (Provider)",
        options=provider_options,
        index=0,
        key="sidebar_provider",
    )

    model_presets: dict[str, list[str]] = {
        "openrouter": [
            "openai/gpt-4o-mini",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "nvidia/nemotron-3.5-lightning:free",
            "cohere/command-r7b-12-2024",
            "liquid/lfm-2.5-2.6b:free",
            "Custom model ID...",
        ],
        "ollama": [
            "qwen2.5:7b",
            "llama3.2:3b",
            "qwen2.5:3b",
            "llama3.1:8b",
            "Custom model ID...",
        ],
        "gemini": ["gemini-2.5-flash", "gemini-3.5-flash", "Custom model ID..."],
        "openai": ["gpt-4o-mini", "gpt-4o", "Custom model ID..."],
        "anthropic": ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest", "Custom model ID..."],
    }

    preset_choice = st.selectbox(
        "Mô hình (Model)",
        options=model_presets.get(selected_provider, ["Custom model ID..."]),
        index=0,
    )
    if preset_choice == "Custom model ID...":
        selected_model = st.text_input("Mã mô hình tùy chỉnh (Model ID)", value="openai/gpt-4o-mini").strip()
    else:
        selected_model = preset_choice

    prov_dot, prov_status_text = check_provider_status(selected_provider)
    st.markdown(
        f"""
        <div class="sb-status-row">
            <span><span class="sb-dot {prov_dot}"></span><strong>{selected_provider}</strong></span>
            <span class="mono" style="color: var(--muted-fg); font-size: 0.72rem;">{prov_status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Cài đặt nâng cao", expanded=False):
        theme_choice = st.selectbox(
            "Giao diện",
            options=["dark", "light"],
            index=0 if st.session_state.theme == "dark" else 1,
            format_func=lambda v: "Tối (Dark)" if v == "dark" else "Sáng (Light)",
        )
        if theme_choice != st.session_state.theme:
            st.session_state.theme = theme_choice
            st.rerun()

        version_options = ["v3", "v2", "v1", "v0", "v3-qwen7b", "v3-llama3b", "v4-local", "v5-local"]
        selected_version = st.selectbox(
            "Phiên bản Artifact",
            options=version_options,
            index=0,
            key="sidebar_version",
        )
        max_tool_rounds = st.slider("Số vòng gọi tool tối đa", min_value=1, max_value=6, value=4)
        history_window = st.slider("Cửa sổ ngữ cảnh (số lượt hội thoại)", min_value=1, max_value=10, value=5)
        auto_save_transcript = st.checkbox("Tự động lưu nhật ký hội thoại", value=True)

        st.caption("Trạng thái sẵn sàng của công cụ")
        for svc_name, dot_cls, svc_status in check_tool_env_readiness():
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; font-size:0.73rem; padding:3px 0; border-bottom:1px solid var(--border);">
                    <span><span class="sb-dot {dot_cls}"></span>{svc_name}</span>
                    <span class="mono" style="color:var(--muted-fg);">{svc_status}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =====================================================================
# ARTIFACT METADATA & TOOL DECLARATIONS
# =====================================================================
artifact_info = build_artifact_version(selected_version, SYSTEM_PROMPT_PATH, TOOLS_YAML_PATH)
tool_declarations = load_tool_declarations(TOOLS_YAML_PATH)
openai_tools = to_openai_tools(tool_declarations)
system_prompt_text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

active_conv = get_active_conversation()


# =====================================================================
# CONFIRMATION HANDLER & DIALOG MODALS
# =====================================================================
def handle_confirmation_decision(
    msg_index: int,
    pending: dict[str, Any],
    approved: bool,
) -> None:
    """Execute or reject a pending confirmation action safely without duplicate execution."""
    conf_id = pending["confirmation_id"]
    if conf_id in st.session_state.executed_confirmations or pending.get("resolved"):
        return

    st.session_state.executed_confirmations.add(conf_id)
    pending["resolved"] = True
    pending["decision"] = "approved" if approved else "rejected"

    target_msg = active_conv["messages"][msg_index]
    turn_idx = target_msg.get("turn_index", len(active_conv["turns"]))

    if approved:
        call = ToolCall(
            name=pending["tool_name"],
            args={"text": pending["text"], "confirmed": True},
        )
        confirmed_event = execute_single_tool(call, allow_confirmed_send=True)
        confirmed_event["round"] = len(target_msg.get("rounds", [])) + 1
        confirmed_event["step"] = len(target_msg.get("tool_events", [])) + 1

        target_msg["tool_events"].append(confirmed_event)
        target_msg["rounds"].append({
            "round": confirmed_event["round"],
            "assistant_text": "User approved confirmation. Executing send with confirmed=True.",
            "tool_calls": [{"name": call.name, "args": call.args}],
            "tool_results": [
                {"tool": confirmed_event["tool"], "args": confirmed_event["args"], "result": confirmed_event["result"]}
            ],
        })

        res = confirmed_event.get("result", {})
        if isinstance(res, dict) and res.get("status") == "sent":
            final_text = (
                f"**Đã xác nhận và gửi thành công lên Telegram.**\n\n"
                f"- **Action:** `{call.name}(confirmed=True)`\n"
                f"- **Destination:** `{pending['destination']}`\n"
                f"- **Sent content:**\n> {pending['text']}"
            )
        else:
            err_name = res.get("error", "ExecutionError")
            err_msg = res.get("message", "Unknown error")
            final_text = (
                f"**Đã xác nhận (`confirmed=True`)**, tuy nhiên công cụ `{call.name}` trả về lỗi môi trường:\n\n"
                f"- **Status:** `{err_name}: {err_msg}`\n"
                f"- **Requested content:**\n> {pending['text']}"
            )
        target_msg["status"] = "answered"
        target_msg["content"] = final_text
    else:
        rejection_text = (
            f"**Đã hủy hành động gửi (`{pending['tool_name']}`).**\n\n"
            f"Bạn đã chọn **Reject**. Không có dữ liệu nào được gửi tới `{pending['destination']}`."
        )
        target_msg["content"] = rejection_text
        target_msg["status"] = "rejected_by_user"
        for ev in target_msg.get("tool_events", []):
            if ev.get("tool") == pending["tool_name"]:
                ev["ui_status"] = "Failed"

    for t in active_conv["turns"]:
        if t["turn_index"] == turn_idx:
            t["status"] = target_msg["status"]
            t["assistant_text"] = target_msg["content"]
            t["rounds"] = target_msg["rounds"]
            t["tool_events"] = target_msg["tool_events"]
            t["ended_at"] = now_iso()
            break

    active_conv["history_pairs"].append({
        "role": "user",
        "content": "[User Approved Confirmation]" if approved else "[User Rejected Confirmation]",
    })
    active_conv["history_pairs"].append({
        "role": "assistant",
        "content": target_msg["content"],
    })

    if auto_save_transcript:
        transcript_payload = build_session_transcript(
            session_id=active_conv["session_id"],
            version_label=selected_version,
            provider_name=selected_provider,
            model_name=selected_model,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
            created_at=active_conv["created_at"],
            turns=active_conv["turns"],
        )
        saved_p = save_session_transcript(transcript_payload)
        active_conv["last_saved_path"] = str(saved_p.relative_to(ROOT))


@st.dialog("Yêu cầu xác nhận hành động", width="small")
def show_confirmation_dialog(msg_index: int, pending: dict[str, Any]) -> None:
    st.markdown(f"**Hành động (Action):** `{pending['tool_name']}` (`{pending['underlying_tool']}`)")
    st.markdown(f"**Đích đến (Destination):** `{pending['destination']}`")
    st.markdown("**Nội dung tin nhắn:**")
    st.code(pending["text"] or "(Nội dung trống)", language="text")
    st.warning(
        "Cơ chế an toàn (Guardrail): `confirmed=True` chỉ được kích hoạt sau khi bạn phê duyệt. "
        "Từ chối sẽ hủy thao tác và không gọi tool."
    )
    col_reject, col_approve = st.columns(2)
    with col_reject:
        if st.button(
            "Từ chối (Reject)",
            key=f"dlg_reject_{pending['confirmation_id']}",
            use_container_width=True,
        ):
            handle_confirmation_decision(msg_index, pending, approved=False)
            st.rerun()
    with col_approve:
        if st.button(
            "Phê duyệt & Gửi",
            key=f"dlg_approve_{pending['confirmation_id']}",
            type="primary",
            use_container_width=True,
        ):
            handle_confirmation_decision(msg_index, pending, approved=True)
            st.rerun()


@st.dialog("Danh mục công cụ (Tool Inventory)", width="large")
def show_tool_inventory_dialog(declarations: list[dict[str, Any]]) -> None:
    core_set = {"clarify", "timeline", "social_search", "lookup", "fetch", "format"}
    bonus_set = {"send", "policy", "papers", "paper_text"}
    md_lines = [
        "| Công cụ (Tool) | Phân loại | Tham số | Mô tả | Trạng thái |",
        "|---|---|---|---|---|",
    ]
    for decl in declarations:
        t_name = decl.get("name", "")
        params = list((decl.get("parameters", {}).get("properties") or {}).keys())
        category = "Cốt lõi" if t_name in core_set else ("Mở rộng" if t_name in bonus_set else "Tùy biến")
        params_str = ", ".join(f"`{p}`" for p in params) if params else "*Không có*"
        desc_str = (decl.get("description", "") or "").replace("|", "\\|").replace("\n", " ")
        impl_str = "Sẵn sàng" if t_name in TOOL_FUNCTIONS else "Chưa có mã nguồn"
        md_lines.append(f"| `{t_name}` | {category} | {params_str} | {desc_str} | {impl_str} |")
    st.markdown("\n".join(md_lines))


# =====================================================================
# MAIN WORKSPACE TOP BAR
# =====================================================================
top_left, top_right = st.columns([3.2, 1.8])
with top_left:
    st.markdown(
        f"""
        <div class="ws-topbar" style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;">
            <div>
                <div class="ws-title">{active_conv['title']}</div>
                <div class="ws-meta-row" style="margin-top: 4px;">
                    <span class="ws-pill"><strong>{selected_provider}</strong></span>
                    <span class="ws-pill">{selected_model}</span>
                    <span class="ws-pill">{artifact_info.artifact_version}</span>
                    <span class="ws-pill">{len(tool_declarations)} công cụ</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_right:
    act_c1, act_c2, act_c3 = st.columns(3)
    with act_c1:
        if st.button("Công cụ", use_container_width=True, help="Xem danh sách công cụ đã đăng ký"):
            show_tool_inventory_dialog(tool_declarations)
    with act_c2:
        if st.button(
            "Lưu",
            use_container_width=True,
            disabled=len(active_conv["turns"]) == 0,
            help="Lưu nhật ký hội thoại vào ổ đĩa",
        ):
            transcript_payload = build_session_transcript(
                session_id=active_conv["session_id"],
                version_label=selected_version,
                provider_name=selected_provider,
                model_name=selected_model,
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
                created_at=active_conv["created_at"],
                turns=active_conv["turns"],
            )
            saved_p = save_session_transcript(transcript_payload)
            active_conv["last_saved_path"] = str(saved_p.relative_to(ROOT))
            st.toast(f"Đã lưu nhật ký: {active_conv['last_saved_path']}")
    with act_c3:
        if st.button("Làm mới", use_container_width=True, help="Xóa hội thoại hiện tại"):
            active_conv["messages"] = []
            active_conv["turns"] = []
            active_conv["history_pairs"] = []
            st.session_state.messages = active_conv["messages"]
            st.rerun()

st.divider()


# =====================================================================
# WELCOME SCREEN (Empty State)
# =====================================================================
if not active_conv["messages"]:
    suggested_prompts = [
        {
            "id": "s1",
            "category": "Nghiên cứu",
            "title": "Tổng hợp tin tức AI mới nhất",
            "prompt": "Tìm tin tức AI mới nhất và tổng hợp 5 thông tin quan trọng nhất.",
            "icon": "search",
        },
        {
            "id": "s1b",
            "category": "Học thuật",
            "title": "Tra cứu bài báo arXiv",
            "prompt": "Tìm các bài báo khoa học trên arXiv về retrieval augmented generation evaluation và tóm tắt 3 bài nổi bật.",
            "icon": "book",
        },
        {
            "id": "s2",
            "category": "Làm rõ yêu cầu",
            "title": "Xử lý câu hỏi mơ hồ",
            "prompt": "Tóm tắt 5 bài đăng mới nhất.",
            "icon": "help",
        },
        {
            "id": "s3",
            "category": "Cơ chế bảo vệ",
            "title": "Xác nhận gửi Telegram",
            "prompt": "Đăng bản tin này lên Telegram: Tổng hợp 5 tin tức AI quan trọng nhất hôm nay.",
            "icon": "shield-alert",
        },
        {
            "id": "s4",
            "category": "Chính sách",
            "title": "Tra cứu quy định nội bộ",
            "prompt": "Theo company policy, đăng bản tin lên Telegram channel có cần xác nhận trước không và quy định trích dẫn nguồn như thế nào?",
            "icon": "shield-check",
        },
        {
            "id": "s5",
            "category": "Đọc sâu",
            "title": "Trích xuất PDF từ arXiv",
            "prompt": "Đọc giúp mình bài báo arXiv 1706.03762, lấy nội dung 2 trang đầu và tóm tắt ý chính.",
            "icon": "file",
        },
    ]

    welcome_event = render_welcome_screen(
        theme=st.session_state.theme,
        provider=selected_provider,
        model=selected_model,
        version=artifact_info.artifact_version,
        tool_count=len(tool_declarations),
        prompts=suggested_prompts,
        key=f"welcome_{active_conv['session_id']}",
    )
    if welcome_event and welcome_event.get("type") == "select_prompt":
        st.session_state.queued_prompt = str(welcome_event.get("prompt") or "")
        st.rerun()


# =====================================================================
# RENDER CONVERSATION HISTORY (st.chat_message + st.session_state.messages)
# =====================================================================
dialog_to_open: tuple[int, dict[str, Any]] | None = None

for msg_idx, msg in enumerate(active_conv["messages"]):
    role = msg["role"]
    with st.chat_message(role):
        if role == "user":
            st.markdown(msg["content"])
        else:
            # 1) Tool Call Inspector (Real React + shadcn/ui component)
            render_tool_inspector(
                theme=st.session_state.theme,
                tool_events=msg.get("tool_events", []),
                final_answer=msg.get("content", ""),
                turn_status=msg.get("status", "answered"),
                turn_index=msg.get("turn_index", msg_idx),
                key=f"inspector_{active_conv['session_id']}_{msg_idx}_{len(msg.get('tool_events', []))}_{msg.get('status', '')}",
            )

            # 2) Assistant Final Answer
            if msg.get("content"):
                st.markdown(msg["content"])

            # 3) Confirmation Interface (React shadcn/ui Card + @st.dialog modal)
            pending_conf = msg.get("pending_confirmation")
            if pending_conf:
                conf_id = pending_conf["confirmation_id"]
                conf_event = render_confirmation_card(
                    theme=st.session_state.theme,
                    pending=pending_conf,
                    msg_index=msg_idx,
                    key=f"conf_{conf_id}_{pending_conf.get('resolved', False)}_{st.session_state.theme}",
                )
                if conf_event:
                    ev_type = conf_event.get("type")
                    if ev_type == "confirm_action":
                        handle_confirmation_decision(
                            msg_idx,
                            pending_conf,
                            approved=bool(conf_event.get("approved")),
                        )
                        st.rerun()
                    elif ev_type == "open_confirm_dialog" and not pending_conf.get("resolved"):
                        dialog_to_open = (msg_idx, pending_conf)

                # Automatically open AlertDialog modal once when a new confirmation is created
                if (
                    not pending_conf.get("resolved")
                    and conf_id not in st.session_state.auto_opened_dialogs
                    and dialog_to_open is None
                ):
                    st.session_state.auto_opened_dialogs.add(conf_id)
                    dialog_to_open = (msg_idx, pending_conf)

            # 4) Clarify Quick Options (React shadcn/ui Buttons)
            if msg_idx == len(active_conv["messages"]) - 1:
                for ev in msg.get("tool_events", []):
                    res = ev.get("result", {})
                    if isinstance(res, dict) and res.get("awaiting_user"):
                        opts = list(res.get("options") or [])
                        if res.get("response_type") == "yes_no" and not opts:
                            opts = ["Đồng ý, xác nhận thực hiện", "Không, hủy bỏ"]
                        if opts:
                            clarify_event = render_clarify_options(
                                theme=st.session_state.theme,
                                options=[str(o) for o in opts],
                                key=f"clarify_{active_conv['session_id']}_{msg_idx}_{st.session_state.theme}",
                            )
                            if clarify_event and clarify_event.get("type") == "select_clarify_option":
                                st.session_state.queued_prompt = str(clarify_event.get("option") or "")
                                st.rerun()

if dialog_to_open is not None:
    show_confirmation_dialog(dialog_to_open[0], dialog_to_open[1])


# =====================================================================
# CHAT INPUT & AGENT EXECUTION
# =====================================================================
chat_input_val = st.chat_input(
    "Nhập câu hỏi nghiên cứu, dán liên kết URL hoặc yêu cầu hành động...",
    disabled=st.session_state.is_processing,
)
user_query = st.session_state.queued_prompt or chat_input_val
if st.session_state.queued_prompt:
    st.session_state.queued_prompt = None

if user_query:
    user_query = user_query.strip()
    if user_query:
        st.session_state.is_processing = True
        try:
            if not active_conv["messages"]:
                active_conv["title"] = user_query[:38] + ("..." if len(user_query) > 38 else "")

            active_conv["messages"].append({"role": "user", "content": user_query})
            st.session_state.messages = active_conv["messages"]

            with st.chat_message("user"):
                st.markdown(user_query)

            turn_index = len(active_conv["turns"]) + 1
            started_at = now_iso()

            messages_payload = [
                {"role": "system", "content": system_prompt_text},
                *trim_history(active_conv["history_pairs"], history_window),
                {"role": "user", "content": user_query},
            ]

            with st.chat_message("assistant"):
                status_box = st.status(
                    f"Đang thực thi ResearchAgent ({selected_provider} / {selected_model})...",
                    expanded=True,
                )
                try:
                    base_provider = make_provider(selected_provider)
                    adapter_provider = UIProviderAdapter(selected_provider, base_provider, max_tokens=1024)
                    _agent_instance = ResearchAgent(
                        adapter_provider,
                        system_prompt=system_prompt_text,
                        tools=openai_tools,
                        model=selected_model,
                    )

                    turn_result = run_interactive_agent_turn(
                        provider=_agent_instance.provider,
                        messages=messages_payload,
                        tools=_agent_instance.tools,
                        model=_agent_instance.model,
                        max_tool_rounds=max_tool_rounds,
                        status_container=status_box,
                    )

                    status_label_map = {
                        "answered": "Hoàn thành lượt trả lời",
                        "waiting_for_user": "Đang chờ người dùng làm rõ",
                        "awaiting_confirmation": "Đang chờ phê duyệt hành động",
                        "max_tool_rounds": "Đạt giới hạn số vòng gọi tool tối đa",
                    }
                    status_box.update(
                        label=status_label_map.get(turn_result["status"], "Lượt xử lý hoàn tất"),
                        state="complete",
                        expanded=False,
                    )

                    assistant_text = turn_result["assistant_text"]
                    tool_events = turn_result["tool_events"]
                    rounds = turn_result["rounds"]
                    pending_conf = turn_result["pending_confirmation"]

                    assistant_msg_record = {
                        "role": "assistant",
                        "content": assistant_text,
                        "status": turn_result["status"],
                        "tool_events": tool_events,
                        "rounds": rounds,
                        "turn_index": turn_index,
                        "pending_confirmation": pending_conf,
                    }
                    active_conv["messages"].append(assistant_msg_record)
                    st.session_state.messages = active_conv["messages"]
                    active_conv["history_pairs"].append({"role": "user", "content": user_query})
                    active_conv["history_pairs"].append({"role": "assistant", "content": assistant_text})

                    turn_record = {
                        "turn_index": turn_index,
                        "started_at": started_at,
                        "user": user_query,
                        "status": turn_result["status"],
                        "assistant_text": assistant_text,
                        "rounds": rounds,
                        "tool_events": tool_events,
                        "ended_at": now_iso(),
                    }
                    active_conv["turns"].append(turn_record)

                    if auto_save_transcript:
                        transcript_payload = build_session_transcript(
                            session_id=active_conv["session_id"],
                            version_label=selected_version,
                            provider_name=selected_provider,
                            model_name=selected_model,
                            history_window=history_window,
                            max_tool_rounds=max_tool_rounds,
                            created_at=active_conv["created_at"],
                            turns=active_conv["turns"],
                        )
                        saved_p = save_session_transcript(transcript_payload)
                        active_conv["last_saved_path"] = str(saved_p.relative_to(ROOT))

                    st.session_state.is_processing = False
                    st.rerun()

                except Exception as exc:
                    err_str = f"{type(exc).__name__}: {str(exc)}"
                    status_box.update(label=f"Lỗi nhà cung cấp: {type(exc).__name__}", state="error", expanded=True)
                    st.error(
                        f"**Yêu cầu thất bại (`{selected_provider}` / `{selected_model}`):**\n\n"
                        f"`{err_str}`\n\n"
                        "Vui lòng kiểm tra kết nối mạng, cấu hình API key trong file `.env` hoặc đổi sang mô hình khác ở thanh bên."
                    )
                    turn_record = {
                        "turn_index": turn_index,
                        "started_at": started_at,
                        "user": user_query,
                        "status": "provider_error",
                        "error": err_str,
                        "assistant_text": None,
                        "rounds": [],
                        "tool_events": [],
                        "ended_at": now_iso(),
                    }
                    active_conv["turns"].append(turn_record)
                    if auto_save_transcript:
                        transcript_payload = build_session_transcript(
                            session_id=active_conv["session_id"],
                            version_label=selected_version,
                            provider_name=selected_provider,
                            model_name=selected_model,
                            history_window=history_window,
                            max_tool_rounds=max_tool_rounds,
                            created_at=active_conv["created_at"],
                            turns=active_conv["turns"],
                        )
                        save_session_transcript(transcript_payload)
        finally:
            st.session_state.is_processing = False
