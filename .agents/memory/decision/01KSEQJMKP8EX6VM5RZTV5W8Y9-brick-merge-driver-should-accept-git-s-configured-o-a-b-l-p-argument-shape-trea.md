---
id: "01KSEQJMKP8EX6VM5RZTV5W8Y9"
title: "Brick merge-driver should accept Git's configured %O %A %B %L %P argument shape, trea..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "implementation-choice"
  - "v1"
  - "conflicts"
  - "git"
  - "merge"
created_at: "2026-05-25T04:51:32Z"
updated_at: "2026-05-25T04:51:32Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "167"
  section: "Settled v1 implementation choices"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "167"
    text: "`brick merge-driver` should accept Git's configured `%O %A %B %L %P` argument shape, treating `%O` as base, `%A` as ours/current and the file to overwrite on successful resolution, `%B` as theirs, and `%P` as the conflicted memory path when present."
confirm_public: true
content_hash: "sha256:e33f45dfef21c9554dc6d9c526d8527d95107af10a2507528aed28437918e608"
---
Migrated from `.agents/MEMORIES.md` line 167 under `Settled v1 implementation choices`.

`brick merge-driver` should accept Git's configured `%O %A %B %L %P` argument shape, treating `%O` as base, `%A` as ours/current and the file to overwrite on successful resolution, `%B` as theirs, and `%P` as the conflicted memory path when present.
