---
name: github_repos
track: bonus
kind: live_api
provider: GitHub REST API (search/repositories)
requires_env: []
inputs: [query, language, sort, limit]
outputs: [items, total_count]
side_effect: false
---
# github_repos

Searches public GitHub repositories. Works without a key (10 search requests /
minute); set optional `GITHUB_TOKEN` in `.env` to raise the limit to 30/min.

- `language`: optional, appended as `language:<x>` to the query (e.g. `python`).
- `sort`: `stars` (default), `updated`, or `best_match` (GitHub relevance, no sort param).
- `limit`: clamped to 1–20; non-numeric values fall back to 5.
- Empty `query` returns an error dict without calling the network.
- HTTP 403/429 (rate limit) returns an error dict.

Each item has `title` (owner/repo), `url`, `source`, `summary` (description),
`stars`, `language`, `updated_at`, `topics` (first 5).
