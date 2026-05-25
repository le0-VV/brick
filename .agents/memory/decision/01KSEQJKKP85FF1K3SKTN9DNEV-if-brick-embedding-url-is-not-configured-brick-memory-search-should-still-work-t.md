---
id: "01KSEQJKKP85FF1K3SKTN9DNEV"
title: "If BRICK_EMBEDDING_URL is not configured, brick memory search should still work throu..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "embeddings"
  - "semantic"
created_at: "2026-05-25T04:51:31Z"
updated_at: "2026-05-25T04:51:31Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "155"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "155"
    text: "If `BRICK_EMBEDDING_URL` is not configured, `brick memory search` should still work through keyword search and report semantic search as unavailable because the environment variable is missing."
confirm_public: true
content_hash: "sha256:aa7116ea22768386d426a2ef0c4a8258223853712365c21ff88e8ba40df2381a"
---
Migrated from `.agents/MEMORIES.md` line 155 under `Settled v1 implementation choices`.

If `BRICK_EMBEDDING_URL` is not configured, `brick memory search` should still work through keyword search and report semantic search as unavailable because the environment variable is missing.
