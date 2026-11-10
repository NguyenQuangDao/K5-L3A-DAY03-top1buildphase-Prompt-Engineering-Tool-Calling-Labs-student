---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API (no key)
requires_env: []
inputs: [query, sort, timeframe, limit]
outputs: [items]
side_effect: false
---
# hn_search

Searches Hacker News stories via the public Algolia API (`/search` for
relevance, `/search_by_date` for newest). No API key needed.

- `sort`: `relevance` (default) or `date`.
- `timeframe`: `day | week | month | year | all` → `numericFilters=created_at_i>now-N`.
- `limit`: clamped to 1–20; non-numeric values fall back to 5.
- Empty `query` returns an error dict without calling the network.

Each item has `title`, `url` (story link, or the HN thread if the story has no
link), `source`, `summary` (points + comments), `hn_url`, `date`, `points`,
`num_comments`.
