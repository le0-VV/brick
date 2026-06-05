---
id: "01KTBQ1JKQ6W6EGE17WG116QZ9"
title: "Gitignore agent TODO plans in every Brick setup"
type: "decision"
status: "active"
tags:
  - "setup"
  - "gitignore"
  - "agents"
  - "todo"
created_at: "2026-06-05T11:00:12Z"
updated_at: "2026-06-05T11:00:12Z"
source:
  kind: "conversation"
  ref: "user setup-wide gitignore instruction"
evidence:
  -
    kind: "quote"
    text: "there's a reason why `.agents/TODO.md` is added to [.gitignore](.gitignore) . It should be the case for all setups that uses brick"
confirm_public: true
content_hash: "sha256:f91ffa684d8c35800e8caa916c972074ce13b8b3221ca24c3ba1d91978ce0fdc"
---
Brick setup should add `.agents/TODO.md` to `.gitignore` for every Brick-enabled repository because agent TODO plans are per-session local working state, not project memory or shared repo state.
