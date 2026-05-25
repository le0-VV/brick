---
id: "01KSEQJMYEGGN0BDP7BDM9PD2A"
title: "Brick memory redact should read a JSON object from stdin, require a canonical memory..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "evidence"
  - "content-hash"
  - "index"
  - "redaction"
created_at: "2026-05-25T04:51:32Z"
updated_at: "2026-05-25T04:51:32Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "171"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "171"
    text: "`brick memory redact` should read a JSON object from stdin, require a canonical memory `path`, a non-empty `redactions` list of exact text values, and a human-readable `reason`, replace every target text with `[REDACTED]`, mark the memory `status: redacted`, append redaction evidence, recompute `updated_at` and `content_hash`, validate before writing, and rebuild the local index by default."
confirm_public: true
content_hash: "sha256:ce09f505cb5e784d0ba9b8cee17e4c9e23102c3b01e1370d0f92eccfbcfa45ca"
---
Migrated from `.agents/MEMORIES.md` line 171 under `Settled v1 implementation choices`.

`brick memory redact` should read a JSON object from stdin, require a canonical memory `path`, a non-empty `redactions` list of exact text values, and a human-readable `reason`, replace every target text with `[REDACTED]`, mark the memory `status: redacted`, append redaction evidence, recompute `updated_at` and `content_hash`, validate before writing, and rebuild the local index by default.
