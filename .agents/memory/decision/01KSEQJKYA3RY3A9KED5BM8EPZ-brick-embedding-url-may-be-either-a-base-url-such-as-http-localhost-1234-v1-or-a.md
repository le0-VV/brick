---
id: "01KSEQJKYA3RY3A9KED5BM8EPZ"
title: "BRICK_EMBEDDING_URL may be either a base URL such as http://localhost:1234/v1 or a fu..."
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
  line: "159"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "159"
    text: "`BRICK_EMBEDDING_URL` may be either a base URL such as `http://localhost:1234/v1` or a full embeddings endpoint; Brick should append `/embeddings` unless the configured path already ends with `/embeddings`."
confirm_public: true
content_hash: "sha256:7a82f6fbd501a6f6d43fc48173774a7356bc683fb283f591b5d18f57920e3610"
---
Migrated from `.agents/MEMORIES.md` line 159 under `Settled v1 implementation choices`.

`BRICK_EMBEDDING_URL` may be either a base URL such as `http://localhost:1234/v1` or a full embeddings endpoint; Brick should append `/embeddings` unless the configured path already ends with `/embeddings`.
