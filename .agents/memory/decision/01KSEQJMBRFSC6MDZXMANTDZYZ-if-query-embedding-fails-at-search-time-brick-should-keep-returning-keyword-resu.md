---
id: "01KSEQJMBRFSC6MDZXMANTDZYZ"
title: "If query embedding fails at search time, Brick should keep returning keyword results..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "embeddings"
  - "semantic"
created_at: "2026-05-25T04:51:32Z"
updated_at: "2026-05-25T04:51:32Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "164"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "164"
    text: "If query embedding fails at search time, Brick should keep returning keyword results and report semantic search as unavailable with the embedding failure reason."
confirm_public: true
content_hash: "sha256:30ed27eb61f20448619d9df10fa9da7d64d4f80de6dcd3e16eab3c2271203429"
---
Migrated from `.agents/MEMORIES.md` line 164 under `Settled v1 implementation choices`.

If query embedding fails at search time, Brick should keep returning keyword results and report semantic search as unavailable with the embedding failure reason.
