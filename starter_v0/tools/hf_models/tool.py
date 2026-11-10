from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, USER_AGENT, clamp_int, err, pick_enum

# Friendly sort names the model sees -> Hugging Face API sort keys.
SORT_KEYS = {"downloads": "downloads", "likes": "likes", "trending": "trendingScore", "recent": "createdAt"}


def search_hf_models(query: str = "", task: str = "", sort: str = "downloads", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        task = (task or "").strip().lower() if isinstance(task, str) else ""
        if not query and not task:
            raise ValueError("query and task are both empty")
        sort = pick_enum(sort, list(SORT_KEYS), "downloads")
        limit = clamp_int(limit, 5, 1, 20)

        params: dict[str, Any] = {"sort": SORT_KEYS[sort], "direction": -1, "limit": limit}
        if query:
            params["search"] = query
        if task:
            params["pipeline_tag"] = task
        response = requests.get("https://huggingface.co/api/models", params=params, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError(f"unexpected response shape: {type(data).__name__}")
        items = []
        for model in data[:limit]:
            model_id = model.get("id") or model.get("modelId")
            if not model_id:
                continue
            downloads = model.get("downloads") or 0
            likes = model.get("likes") or 0
            items.append({
                "title": model_id,
                "url": f"https://huggingface.co/{model_id}",
                "source": "huggingface.co",
                "summary": f"{model.get('pipeline_tag') or 'unknown task'} - {downloads:,} downloads, {likes:,} likes",
                "task": model.get("pipeline_tag"),
                "downloads": downloads,
                "likes": likes,
                "created_at": model.get("createdAt"),
            })
        return {"tool": "hf_models", "query": query, "task": task or None, "sort": sort, "items": items}
    except Exception as exc:
        return err("hf_models", exc)
