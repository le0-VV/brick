---
id: "01KSEQJJ95CMART8WNTH63J52Y"
title: "Brick memory add should generate id, created_at, updated_at, content_hash, and the UL..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "content-hash"
created_at: "2026-05-25T04:51:30Z"
updated_at: "2026-05-25T04:51:30Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "139"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "139"
    text: "`brick memory add` should generate `id`, `created_at`, `updated_at`, `content_hash`, and the ULID-slug filename when those are not supplied by the candidate."
confirm_public: true
content_hash: "sha256:fe8ab4c5e60a3a8abb6867b5c50de63249016b6a51b007482cd310e74b7cdd75"
---
Migrated from `.agents/MEMORIES.md` line 139 under `Settled v1 implementation choices`.

`brick memory add` should generate `id`, `created_at`, `updated_at`, `content_hash`, and the ULID-slug filename when those are not supplied by the candidate.
