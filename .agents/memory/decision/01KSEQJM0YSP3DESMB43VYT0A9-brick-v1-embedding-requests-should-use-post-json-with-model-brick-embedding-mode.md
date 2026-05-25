---
id: "01KSEQJM0YSP3DESMB43VYT0A9"
title: "Brick v1 embedding requests should use POST JSON with {model: BRICK_EMBEDDING_MODEL..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "embeddings"
created_at: "2026-05-25T04:51:31Z"
updated_at: "2026-05-25T04:51:31Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "160"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "160"
    text: "Brick v1 embedding requests should use `POST` JSON with `{\"model\": BRICK_EMBEDDING_MODEL, \"input\": [text, ...]}` and should expect an OpenAI-compatible response whose `data` items contain numeric `embedding` arrays in input order."
confirm_public: true
content_hash: "sha256:26d000ebb0ebb401b4b20d213aabd5216482a4453368cf7c510ff6060daf6c12"
---
Migrated from `.agents/MEMORIES.md` line 160 under `Settled v1 implementation choices`.

Brick v1 embedding requests should use `POST` JSON with `{"model": BRICK_EMBEDDING_MODEL, "input": [text, ...]}` and should expect an OpenAI-compatible response whose `data` items contain numeric `embedding` arrays in input order.
