---
id: "01KSEQJG623MF1GRW6YSGCSC62"
title: "Content_hash should be based on normalized memory content while excluding volatile fi..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "content-hash"
created_at: "2026-05-25T04:51:28Z"
updated_at: "2026-05-25T04:51:28Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "114"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "114"
    text: "`content_hash` should be based on normalized memory content while excluding volatile fields such as `content_hash` itself and `updated_at`."
confirm_public: true
content_hash: "sha256:c6b995ebba1662d01cf57fe32730a685237be009c3c6a052d0a3ca223cc64cdf"
---
Migrated from `.agents/MEMORIES.md` line 114 under `Settled v1 implementation choices`.

`content_hash` should be based on normalized memory content while excluding volatile fields such as `content_hash` itself and `updated_at`.
