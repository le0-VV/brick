---
id: "01KSEQJANZ7XW3VNJFYBSQNVJ8"
title: "When Brick blocks a memory candidate, the script should return a machine-readable str..."
type: "decision"
status: "active"
tags:
  - "migrated"
  - "product-direction"
  - "redaction"
created_at: "2026-05-25T04:51:22Z"
updated_at: "2026-05-25T04:51:22Z"
source:
  kind: "file"
  path: ".agents/MEMORIES.md"
  line: "42"
  section: "Product direction: repo-local project memory system"
evidence:
  -
    kind: "file_excerpt"
    path: ".agents/MEMORIES.md"
    line: "42"
    text: "When Brick blocks a memory candidate, the script should return a machine-readable structured response with fields such as `status`, `reason`, redacted `matches`, and available `actions` like `redact`, `confirm_public`, and `reject`."
confirm_public: true
content_hash: "sha256:74888693959c5cb6d51e4e96f48a5d45863208fccd2ded7bfa3d21a38820aebd"
---
Migrated from `.agents/MEMORIES.md` line 42 under `Product direction: repo-local project memory system`.

When Brick blocks a memory candidate, the script should return a machine-readable structured response with fields such as `status`, `reason`, redacted `matches`, and available `actions` like `redact`, `confirm_public`, and `reject`.
