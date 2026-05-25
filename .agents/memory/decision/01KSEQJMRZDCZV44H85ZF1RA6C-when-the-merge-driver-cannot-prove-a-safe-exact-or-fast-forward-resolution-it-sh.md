---
id: "01KSEQJMRZDCZV44H85ZF1RA6C"
title: "When the merge driver cannot prove a safe exact or fast-forward resolution, it should..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "conflicts"
  - "merge"
created_at: "2026-05-25T04:51:32Z"
updated_at: "2026-05-25T04:51:32Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "169"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "169"
    text: "When the merge driver cannot prove a safe exact or fast-forward resolution, it should write a conflict report and exit nonzero without silently editing the canonical memory."
confirm_public: true
content_hash: "sha256:e1dbf81fd77dde439623bb739c4e1d70764f30cf5c6eafca360957650fbb1ed3"
---
Migrated from `.agents/MEMORIES.md` line 169 under `Settled v1 implementation choices`.

When the merge driver cannot prove a safe exact or fast-forward resolution, it should write a conflict report and exit nonzero without silently editing the canonical memory.
