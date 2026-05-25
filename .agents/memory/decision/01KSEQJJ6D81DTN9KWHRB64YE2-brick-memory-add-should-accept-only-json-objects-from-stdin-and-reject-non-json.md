---
id: "01KSEQJJ6D81DTN9KWHRB64YE2"
title: "Brick memory add should accept only JSON objects from stdin and reject non-JSON input..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
created_at: "2026-05-25T04:51:30Z"
updated_at: "2026-05-25T04:51:30Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "138"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "138"
    text: "`brick memory add` should accept only JSON objects from stdin and reject non-JSON input or unknown top-level fields."
confirm_public: true
content_hash: "sha256:d8148666853a2ed0fd051e97a38b485f393717415a532aa7cb432fbaa177736c"
---
Migrated from `.agents/MEMORIES.md` line 138 under `Settled v1 implementation choices`.

`brick memory add` should accept only JSON objects from stdin and reject non-JSON input or unknown top-level fields.
