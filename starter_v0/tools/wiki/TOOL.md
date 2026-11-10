---
name: wiki
track: bonus
kind: live_api
provider: Wikipedia MediaWiki API (no key)
requires_env: []
inputs: [query, lang, max_results]
outputs: [items]
side_effect: false
---
# wiki

Searches Wikipedia and returns the intro paragraph (plain text) of the best
matching articles in one request (`generator=search` + `prop=extracts|info`).
No API key needed; requests send a descriptive `User-Agent` as Wikipedia asks.

- `lang`: `en` (default) or `vi`; anything else falls back to `en`.
- `max_results`: clamped to 1–5 (default 1).
- Extracts are truncated to 1500 characters.
- Results are re-sorted by search rank (`index`) because the API returns them unordered.
- Empty `query` returns an error dict without calling the network.

Good for stable background/definitions ("X là gì?"), not for news.
