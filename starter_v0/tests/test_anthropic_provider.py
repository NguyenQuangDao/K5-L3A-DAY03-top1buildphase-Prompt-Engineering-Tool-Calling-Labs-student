"""Offline test for the Anthropic provider: checks the request we build, no real API call."""
from __future__ import annotations

from types import SimpleNamespace

import anthropic

from providers.anthropic_provider import AnthropicProvider


def test_anthropic_request_has_no_sampling_params_and_maps_tool_calls(monkeypatch) -> None:
    sent: dict = {}

    class FakeMessages:
        def create(self, **kwargs):
            sent.update(kwargs)
            return SimpleNamespace(content=[
                SimpleNamespace(type="thinking", thinking=""),  # thinking block must be skipped
                SimpleNamespace(type="tool_use", name="timeline", input={"screenname": "sama"}),
            ])

    class FakeClient:
        def __init__(self, api_key: str) -> None:
            self.messages = FakeMessages()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    tools = [{"type": "function", "function": {"name": "timeline", "description": "d", "parameters": {"type": "object"}}}]

    response = AnthropicProvider().complete(
        [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}],
        tools, temperature=0.0, tool_choice="required",
    )

    assert sent["model"] == "claude-haiku-5-5"
    assert "temperature" not in sent
    assert sent["max_tokens"] >= 4096
    assert sent["system"] == "sys"
    assert sent["tool_choice"] == {"type": "any"}
    assert sent["tools"][0]["input_schema"] == {"type": "object"}
    assert [(call.name, call.args) for call in response.tool_calls] == [("timeline", {"screenname": "sama"})]
    assert response.text is None
