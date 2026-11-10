from __future__ import annotations

import time
from typing import Any

import requests

from tools._shared import TIMEOUT, USER_AGENT, clamp_int, domain, err, pick_enum

API = "https://hn.algolia.com/api/v1"
SORTS = ["relevance", "date"]
TIMEFRAMES = {"day": 86_400, "week": 7 * 86_400, "month": 30 * 86_400, "year": 365 * 86_400, "all": 0}


def _story_item(hit: dict[str, Any]) -> dict[str, Any]:
    hn_url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
    url = hit.get("url") or hn_url
    points = hit.get("points") or 0
    comments = hit.get("num_comments") or 0
    return {
        "title": hit.get("title"),
        "url": url,
        "source": domain(url) if hit.get("url") else "news.ycombinator.com",
        "summary": f"{points} points, {comments} comments on Hacker News",
        "hn_url": hn_url,
        "date": hit.get("created_at"),
        "points": points,
        "num_comments": comments,
    }


def search_hacker_news(query: str = "", sort: str = "relevance", timeframe: str = "all", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query is empty")
        sort = pick_enum(sort, SORTS, "relevance")
        timeframe = pick_enum(timeframe, list(TIMEFRAMES), "all")
        limit = clamp_int(limit, 5, 1, 20)

        params: dict[str, Any] = {"query": query, "tags": "story", "hitsPerPage": limit}
        if TIMEFRAMES[timeframe]:
            params["numericFilters"] = f"created_at_i>{int(time.time()) - TIMEFRAMES[timeframe]}"
        endpoint = "search" if sort == "relevance" else "search_by_date"
        response = requests.get(f"{API}/{endpoint}", params=params, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        response.raise_for_status()
        hits = response.json().get("hits") or []
        items = [_story_item(hit) for hit in hits if hit.get("title")][:limit]
        return {"tool": "hn_search", "query": query, "sort": sort, "timeframe": timeframe, "items": items}
    except Exception as exc:
        return err("hn_search", exc)
