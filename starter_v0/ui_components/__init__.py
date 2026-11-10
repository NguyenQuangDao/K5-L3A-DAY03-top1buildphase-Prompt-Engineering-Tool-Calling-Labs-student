from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"

if not FRONTEND_DIST.exists() or not (FRONTEND_DIST / "index.html").exists():
    raise RuntimeError(
        f"Missing built React shadcn/ui bundle at {FRONTEND_DIST}. "
        "Run `npm run build` inside `starter_v0/ui_components/frontend`."
    )

_shadcn_component = components.declare_component(
    "research_agent_shadcn_ui",
    path=str(FRONTEND_DIST),
)


def consume_component_event(event: Any) -> dict[str, Any] | None:
    """Return event dict exactly once by deduplicating on `event_id` in session_state."""
    if not isinstance(event, dict):
        return None
    event_id = event.get("event_id")
    if not event_id:
        return None
    handled: set[str] = st.session_state.setdefault("handled_component_events", set())
    if event_id in handled:
        return None
    handled.add(event_id)
    return event


def render_welcome_screen(
    *,
    theme: str,
    provider: str,
    model: str,
    version: str,
    tool_count: int,
    prompts: list[dict[str, str]],
    key: str = "welcome_screen",
) -> dict[str, Any] | None:
    raw = _shadcn_component(
        mode="welcome_screen",
        theme=theme,
        provider=provider,
        model=model,
        version=version,
        toolCount=tool_count,
        prompts=prompts,
        key=key,
        default=None,
    )
    return consume_component_event(raw)


def render_tool_inspector(
    *,
    theme: str,
    tool_events: list[dict[str, Any]],
    final_answer: str | None,
    turn_status: str,
    turn_index: int,
    key: str,
) -> None:
    _shadcn_component(
        mode="tool_inspector",
        theme=theme,
        toolEvents=tool_events,
        finalAnswer=final_answer,
        turnStatus=turn_status,
        turnIndex=turn_index,
        key=key,
        default=None,
    )


def render_confirmation_card(
    *,
    theme: str,
    pending: dict[str, Any],
    msg_index: int,
    key: str,
) -> dict[str, Any] | None:
    raw = _shadcn_component(
        mode="confirmation_card",
        theme=theme,
        pending=pending,
        msgIndex=msg_index,
        key=key,
        default=None,
    )
    return consume_component_event(raw)


def render_clarify_options(
    *,
    theme: str,
    options: list[str],
    key: str,
) -> dict[str, Any] | None:
    raw = _shadcn_component(
        mode="clarify_options",
        theme=theme,
        options=options,
        key=key,
        default=None,
    )
    return consume_component_event(raw)
