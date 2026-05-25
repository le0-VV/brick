---
id: "01KSEQJM3NC58JP99V45TG906V"
title: "When embeddings are configured, brick rebuild should store vectors in a generated SQL..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "embeddings"
  - "content-hash"
  - "sqlite"
created_at: "2026-05-25T04:51:32Z"
updated_at: "2026-05-25T04:51:32Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "161"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "161"
    text: "When embeddings are configured, `brick rebuild` should store vectors in a generated SQLite `embeddings` table keyed by memory id and content hash, including model, dimensions, and vector JSON."
confirm_public: true
content_hash: "sha256:1924593ebfc29c59b13b3c74526569eb74d1b2077a4061ccc4f139942560b311"
---
Migrated from `.agents/MEMORIES.md` line 161 under `Settled v1 implementation choices`.

When embeddings are configured, `brick rebuild` should store vectors in a generated SQLite `embeddings` table keyed by memory id and content hash, including model, dimensions, and vector JSON.
