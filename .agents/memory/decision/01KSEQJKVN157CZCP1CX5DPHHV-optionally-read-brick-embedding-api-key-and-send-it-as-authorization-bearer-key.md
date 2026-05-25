---
id: "01KSEQJKVN157CZCP1CX5DPHHV"
title: "Optionally read BRICK_EMBEDDING_API_KEY and send it as Authorization: Bearer <key> fo..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "api"
  - "embeddings"
created_at: "2026-05-25T04:51:31Z"
updated_at: "2026-05-25T04:51:31Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "158"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "158"
    text: "Brick v1 should optionally read `BRICK_EMBEDDING_API_KEY` and send it as `Authorization: Bearer <key>` for API-backed OpenAI-compatible embedding endpoints."
confirm_public: true
content_hash: "sha256:b12bb26ee1e5b4f71181e83e2619d8ce887b9311a2506a02b044ec2314331ec8"
---
Migrated from `.agents/MEMORIES.md` line 158 under `Settled v1 implementation choices`.

Brick v1 should optionally read `BRICK_EMBEDDING_API_KEY` and send it as `Authorization: Bearer <key>` for API-backed OpenAI-compatible embedding endpoints.
