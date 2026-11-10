from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, USER_AGENT, clamp_int, err, pick_enum

LANGS = ["en", "vi"]
MAX_EXTRACT_CHARS = 1500


def wiki_summary(query: str = "", lang: str = "en", max_results: int = 1) -> dict[str, Any]:
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query is empty")
        lang = pick_enum(lang, LANGS, "en")
        max_results = clamp_int(max_results, 1, 1, 5)

        # One request: search + intro extract + canonical URL for each hit.
        response = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "formatversion": 2,
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": max_results,
                "prop": "extracts|info",
                "exintro": 1,
                "explaintext": 1,
                "exlimit": max_results,
                "inprop": "url",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or []
        pages = sorted(pages, key=lambda page: page.get("index", 0))  # API returns pages unordered
        items = []
        for page in pages[:max_results]:
            extract = (page.get("extract") or "").strip()
            if len(extract) > MAX_EXTRACT_CHARS:
                extract = extract[: MAX_EXTRACT_CHARS - 3] + "..."
            items.append({
                "title": page.get("title"),
                "url": page.get("fullurl") or f"https://{lang}.wikipedia.org/wiki/{page.get('title', '').replace(' ', '_')}",
                "source": f"{lang}.wikipedia.org",
                "summary": extract,
            })
        return {"tool": "wiki", "query": query, "lang": lang, "items": items}
    except Exception as exc:
        return err("wiki", exc)
