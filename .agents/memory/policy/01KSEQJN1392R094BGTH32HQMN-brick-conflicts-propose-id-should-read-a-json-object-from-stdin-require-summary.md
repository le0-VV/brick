---
id: "01KSEQJN1392R094BGTH32HQMN"
title: "Brick conflicts propose <id> should read a JSON object from stdin, require summary an..."
type: "policy"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "conflicts"
created_at: "2026-05-25T04:51:33Z"
updated_at: "2026-05-25T04:51:33Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "172"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "172"
    text: "`brick conflicts propose <id>` should read a JSON object from stdin, require `summary` and `memory_markdown`, optionally accept `notes`, validate the proposed memory Markdown, and update only the local conflict report's `proposed_resolution` field so human review remains required before any canonical memory is written."
confirm_public: true
content_hash: "sha256:343ca468fdd5e4831988a81a881b82025e84e2714d323c1cc9a3910c320c6d07"
---
Migrated from `.agents/MEMORIES.md` line 172 under `Settled v1 implementation choices`.

`brick conflicts propose <id>` should read a JSON object from stdin, require `summary` and `memory_markdown`, optionally accept `notes`, validate the proposed memory Markdown, and update only the local conflict report's `proposed_resolution` field so human review remains required before any canonical memory is written.
