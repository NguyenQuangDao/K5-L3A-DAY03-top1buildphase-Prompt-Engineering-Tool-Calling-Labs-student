"""Tool Unit Test Challenge.

Patterns come from test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]

hn_tool = TOOL_FUNCTIONS["hn_search"]
wiki_tool = TOOL_FUNCTIONS["wiki"]
github_tool = TOOL_FUNCTIONS["github_repos"]
hf_tool = TOOL_FUNCTIONS["hf_models"]


def _tweet(tweet_id: str | None, handle: str = "sama", text: str = "hello") -> dict:
    raw = {"screen_name": handle, "text": text, "created_at": "2026-11-10"}
    if tweet_id is not None:
        raw["tweet_id"] = tweet_id
    return raw


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["Sam Altman", "Elon Musk"]
    result = clarify_tool(question="Bạn muốn xem tài khoản nào?", response_type="choice", options=options)

    assert result["options"] == options
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("a2") < markdown.index("## B")  # a2 is grouped under A, not appended last


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}", "url": f"https://example.com/{i}"} for i in range(3)]
    lines = format_tool(items=items, template="thread")["markdown"].split("\n\n")

    assert [line.split(" ", 1)[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = format_tool(items=empty, template="sections")
        assert result["item_count"] == 0


def test_format_string_items_from_model_are_rendered_not_crashed() -> None:
    # Regression: items=["..."] used to raise AttributeError ('str' object has no attribute 'get').
    result = format_tool(items=["Tin một", "Tin hai", ""], template="bullets")

    assert result["item_count"] == 2
    assert "- Tin một" in result["markdown"]
    assert "- Tin hai" in result["markdown"]


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@test_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:abc/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "@test_channel"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


def test_send_string_false_confirmation_does_not_send(monkeypatch, fake_http) -> None:
    # Regression: `if not confirmed` treated the string "false" as truthy and posted the message.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@test_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    for value in ("false", "False", "no", "0", 1, None):
        assert send_tool(text="x", confirmed=value)["status"] == "needs_confirmation"
    assert calls == []


def test_send_string_true_confirmation_is_accepted(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@test_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    assert send_tool(text="x", confirmed="true")["status"] == "sent"
    assert len(calls) == 1


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "AI"


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Body",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = fetch_tool(url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-test"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.example.com/post", "source": "example.com", "summary": "# Body",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    item = fetch_tool(url="https://example.com")["items"][0]

    assert len(item["summary"]) == 4000
    assert item["title"] == "https://example.com"  # falls back to the URL when there is no title


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": [_tweet(None)] + [_tweet(str(i)) for i in range(6)]}))

    result = timeline_tool(screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "rk"
    assert [item["url"] for item in result["items"]] == [f"https://x.com/sama/status/{i}" for i in range(3)]


def test_timeline_negative_limit_does_not_slice_from_end(monkeypatch, fake_http) -> None:
    # Regression: items[: int(-1 or 5)] == items[:-1] returned everything except the last tweet.
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": [_tweet(str(i)) for i in range(6)]}))

    assert len(timeline_tool(screenname="sama", limit=-1)["items"]) == 1
    assert len(timeline_tool(screenname="sama", limit="3")["items"]) == 3


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": [_tweet("1", handle="openai")]}))

    result = social_search_tool(query="OpenAI", search_type="Top", limit=5)

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert result["items"][0]["source"] == "@openai"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    for query in ("", "   ", "và của"):  # only whitespace / Vietnamese stopwords
        assert policy_tool(query=query)["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy_tool(query="data privacy API key prompt", policy_area="data_privacy", top_k=10)["results"]

    assert results
    assert all(item["policy_area"] == "data_privacy" for item in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy_tool(query="citation viral tweet", policy_area="source_citation", top_k=10)["results"]

    untrusted = [line for item in results for line in item["untrusted_text"]]
    assert any("viral tweet as verified" in line for line in untrusted)
    assert not any("viral tweet as verified" in item["facts"] for item in results)


# =====================================================================
# Team tools: hn_search, wiki, github_repos, hf_models
# Each has: happy path (request + mapping), bad input from model, failure path.
# =====================================================================

# ---------------- hn_search ----------------

HN_HIT = {
    "objectID": "42", "title": "LLM agents in practice", "url": "https://www.example.com/agents",
    "points": 520, "num_comments": 239, "created_at": "2026-10-18T20:48:14Z",
}


def test_hn_search_sends_expected_request_and_maps_hits(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [HN_HIT, {"objectID": "43", "title": None}]}))

    result = hn_tool(query="LLM agents", limit=3)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"] == {"query": "LLM agents", "tags": "story", "hitsPerPage": 3}
    assert "User-Agent" in calls[0]["headers"]
    assert result["items"] == [{
        "title": "LLM agents in practice", "url": "https://www.example.com/agents", "source": "example.com",
        "summary": "520 points, 239 comments on Hacker News", "hn_url": "https://news.ycombinator.com/item?id=42",
        "date": "2026-10-18T20:48:14Z", "points": 520, "num_comments": 239,
    }]  # hit without title is skipped


def test_hn_search_date_sort_and_timeframe_build_filter(monkeypatch, fake_http) -> None:
    import tools.hn_search.tool as hn_module
    monkeypatch.setattr(hn_module.time, "time", lambda: 1_000_000.0)
    calls = fake_http(FakeResponse({"hits": []}))

    hn_tool(query="rust", sort="date", timeframe="week")

    assert calls[0]["url"].endswith("/search_by_date")
    assert calls[0]["params"]["numericFilters"] == f"created_at_i>{1_000_000 - 7 * 86_400}"


def test_hn_search_story_without_url_links_to_hn_thread(fake_http) -> None:
    fake_http(FakeResponse({"hits": [{**HN_HIT, "url": None}]}))

    item = hn_tool(query="Ask HN")["items"][0]

    assert item["url"] == "https://news.ycombinator.com/item?id=42"
    assert item["source"] == "news.ycombinator.com"


def test_hn_search_bad_args_from_model_fall_back_to_defaults(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    result = hn_tool(query="ai", sort="popular", timeframe="forever", limit="abc")

    assert result["sort"] == "relevance" and result["timeframe"] == "all"
    assert calls[0]["url"].endswith("/search")
    assert calls[0]["params"]["hitsPerPage"] == 5
    assert "numericFilters" not in calls[0]["params"]


def test_hn_search_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    for query in ("", "   ", None, 123):
        assert hn_tool(query=query)["error"] == "ValueError"
    assert calls == []


def test_hn_search_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("timed out"))
    result = hn_tool(query="ai")
    assert result == {"tool": "hn_search", "error": "Timeout", "message": "timed out"}


# ---------------- wiki ----------------

def test_wiki_returns_pages_in_search_rank_order(fake_http) -> None:
    calls = fake_http(FakeResponse({"query": {"pages": [
        {"index": 2, "title": "Vector database", "extract": "B", "fullurl": "https://en.wikipedia.org/wiki/Vector_database"},
        {"index": 1, "title": "Retrieval-augmented generation", "extract": "A",
         "fullurl": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"},
    ]}}))

    result = wiki_tool(query="RAG", max_results=2)

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[0]["params"]["gsrsearch"] == "RAG"
    assert calls[0]["params"]["gsrlimit"] == 2
    assert "User-Agent" in calls[0]["headers"]
    assert [item["title"] for item in result["items"]] == ["Retrieval-augmented generation", "Vector database"]
    assert result["items"][0]["source"] == "en.wikipedia.org"


def test_wiki_truncates_long_extract(fake_http) -> None:
    fake_http(FakeResponse({"query": {"pages": [{"index": 1, "title": "T", "extract": "x" * 3000}]}}))

    item = wiki_tool(query="T")["items"][0]

    assert len(item["summary"]) == 1500 and item["summary"].endswith("...")
    assert item["url"] == "https://en.wikipedia.org/wiki/T"  # fallback when fullurl is missing


def test_wiki_vi_lang_hits_vietnamese_wikipedia_and_bad_lang_falls_back(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    assert wiki_tool(query="Hà Nội", lang="VI")["items"] == []  # no "query" key = no results, not a crash
    wiki_tool(query="Hanoi", lang="fr", max_results=99)

    assert calls[0]["url"] == "https://vi.wikipedia.org/w/api.php"
    assert calls[1]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[1]["params"]["gsrlimit"] == 5  # clamped


def test_wiki_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    assert wiki_tool(query="")["error"] == "ValueError"
    assert calls == []


def test_wiki_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    assert wiki_tool(query="AI")["error"] == "HTTPError"


# ---------------- github_repos ----------------

GH_REPO = {
    "full_name": "org/agent", "html_url": "https://github.com/org/agent", "description": "An agent",
    "stargazers_count": 1234, "language": "Python", "updated_at": "2026-11-01T00:00:00Z",
    "topics": ["a", "b", "c", "d", "e", "f"],
}


def test_github_repos_sends_language_qualifier_and_maps_repo(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({"total_count": 1, "items": [GH_REPO]}))

    result = github_tool(query="llm agent", language="python", limit=3)

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "llm agent language:python", "per_page": 3, "sort": "stars", "order": "desc"}
    assert "Authorization" not in calls[0]["headers"]
    assert result["total_count"] == 1
    assert result["items"][0] == {
        "title": "org/agent", "url": "https://github.com/org/agent", "source": "github.com", "summary": "An agent",
        "stars": 1234, "language": "Python", "updated_at": "2026-11-01T00:00:00Z", "topics": ["a", "b", "c", "d", "e"],
    }


def test_github_repos_best_match_omits_sort_and_token_is_sent(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    calls = fake_http(FakeResponse({"total_count": 0, "items": []}))

    github_tool(query="rag", sort="best_match")

    assert "sort" not in calls[0]["params"]
    assert calls[0]["headers"]["Authorization"] == "Bearer ghp_test"


def test_github_repos_bad_args_from_model(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({"items": [{**GH_REPO, "description": None}]}))

    assert github_tool(query="")["error"] == "ValueError"
    assert calls == []

    result = github_tool(query="agent", language=None, sort="popularity", limit=0)
    assert calls[0]["params"]["q"] == "agent"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 1
    assert result["items"][0]["summary"] == ""


def test_github_repos_rate_limit_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    fake_http(FakeResponse(status_code=403))
    result = github_tool(query="agent")
    assert result["tool"] == "github_repos"
    assert result["error"] == "HTTPError"


# ---------------- hf_models ----------------

HF_MODEL = {
    "id": "Qwen/Qwen3-0.6B", "likes": 1888, "downloads": 20728069,
    "pipeline_tag": "text-generation", "createdAt": "2025-04-27T03:40:08.000Z",
}


def test_hf_models_sends_expected_request_and_maps_model(fake_http) -> None:
    calls = fake_http(FakeResponse([HF_MODEL, {"likes": 1}]))

    result = hf_tool(query="qwen", task="text-generation", sort="trending", limit=2)

    assert calls[0]["url"] == "https://huggingface.co/api/models"
    assert calls[0]["params"] == {
        "sort": "trendingScore", "direction": -1, "limit": 2, "search": "qwen", "pipeline_tag": "text-generation",
    }
    assert result["items"] == [{
        "title": "Qwen/Qwen3-0.6B", "url": "https://huggingface.co/Qwen/Qwen3-0.6B", "source": "huggingface.co",
        "summary": "text-generation - 20,728,069 downloads, 1,888 likes", "task": "text-generation",
        "downloads": 20728069, "likes": 1888, "created_at": "2025-04-27T03:40:08.000Z",
    }]  # model without id is skipped


def test_hf_models_task_only_query_is_allowed(fake_http) -> None:
    calls = fake_http(FakeResponse([]))

    result = hf_tool(query="", task="Automatic-Speech-Recognition")

    assert "search" not in calls[0]["params"]
    assert calls[0]["params"]["pipeline_tag"] == "automatic-speech-recognition"
    assert result["items"] == []


def test_hf_models_bad_args_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse([]))

    assert hf_tool(query="", task="")["error"] == "ValueError"
    assert calls == []

    hf_tool(query="llama", sort="best", limit="7")
    assert calls[0]["params"]["sort"] == "downloads"
    assert calls[0]["params"]["limit"] == 7


def test_hf_models_unexpected_response_shape_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"error": "Invalid sort"}))
    result = hf_tool(query="qwen")
    assert result["error"] == "ValueError"
    assert "unexpected response shape" in result["message"]


def test_hf_models_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))
    assert hf_tool(query="qwen")["error"] == "HTTPError"
