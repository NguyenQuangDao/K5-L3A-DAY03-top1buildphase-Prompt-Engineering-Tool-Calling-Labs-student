---
name: hf_models
track: bonus
kind: live_api
provider: Hugging Face Hub API (no key)
requires_env: []
inputs: [query, task, sort, limit]
outputs: [items]
side_effect: false
---
# hf_models

Searches models on the Hugging Face Hub (`GET /api/models`). No key needed.

- `query`: free text matched against the model id (e.g. `qwen`, `whisper`).
- `task`: optional pipeline tag (e.g. `text-generation`, `automatic-speech-recognition`,
  `text-to-image`, `feature-extraction`). Either `query` or `task` must be set.
- `sort`: `downloads` (default), `likes`, `trending`, `recent` → mapped to
  `downloads | likes | trendingScore | createdAt`, always descending.
- `limit`: clamped to 1–20; non-numeric values fall back to 5.

Each item has `title` (model id), `url`, `source`, `summary`, `task`,
`downloads`, `likes`, `created_at`.
