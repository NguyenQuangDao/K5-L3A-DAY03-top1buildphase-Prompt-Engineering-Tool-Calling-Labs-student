from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, USER_AGENT, clamp_int, err, pick_enum

SORTS = ["stars", "updated", "best_match"]


def search_github_repos(query: str = "", language: str = "", sort: str = "stars", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query is empty")
        language = (language or "").strip() if isinstance(language, str) else ""
        sort = pick_enum(sort, SORTS, "stars")
        limit = clamp_int(limit, 5, 1, 20)

        q = f"{query} language:{language}" if language else query
        params: dict[str, Any] = {"q": q, "per_page": limit}
        if sort != "best_match":
            params.update({"sort": sort, "order": "desc"})
        headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
        token = os.getenv("GITHUB_TOKEN")  # optional: raises the search rate limit from 10 to 30 req/min
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get("https://api.github.com/search/repositories", params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        items = [{
            "title": repo.get("full_name"),
            "url": repo.get("html_url"),
            "source": "github.com",
            "summary": repo.get("description") or "",
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "updated_at": repo.get("updated_at"),
            "topics": (repo.get("topics") or [])[:5],
        } for repo in (data.get("items") or [])[:limit]]
        return {
            "tool": "github_repos", "query": query, "language": language or None, "sort": sort,
            "total_count": data.get("total_count"), "items": items,
        }
    except Exception as exc:
        return err("github_repos", exc)
