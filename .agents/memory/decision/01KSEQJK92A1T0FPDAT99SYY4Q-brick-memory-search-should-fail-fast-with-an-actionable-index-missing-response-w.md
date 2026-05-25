---
id: "01KSEQJK92A1T0FPDAT99SYY4Q"
title: "Brick memory search should fail fast with an actionable index_missing response when t..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "index"
  - "sqlite"
created_at: "2026-05-25T04:51:31Z"
updated_at: "2026-05-25T04:51:31Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "151"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "151"
    text: "`brick memory search` should fail fast with an actionable `index_missing` response when the SQLite index has not been built instead of silently scanning Markdown."
confirm_public: true
content_hash: "sha256:0275567c0d2d1a953447e3ab7630c49dc16ab7eb7630147ba9e90d5ee0e478d3"
---
Migrated from `.agents/MEMORIES.md` line 151 under `Settled v1 implementation choices`.

`brick memory search` should fail fast with an actionable `index_missing` response when the SQLite index has not been built instead of silently scanning Markdown.
