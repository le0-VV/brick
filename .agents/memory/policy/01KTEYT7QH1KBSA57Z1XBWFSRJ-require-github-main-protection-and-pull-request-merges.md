---
id: "01KTEYT7QH1KBSA57Z1XBWFSRJ"
title: "Require GitHub main protection and pull-request merges"
type: "policy"
status: "active"
tags:
  - "agents"
  - "github"
  - "git"
  - "branch-protection"
  - "pull-request"
  - "setup"
created_at: "2026-06-06T17:13:43Z"
updated_at: "2026-06-06T17:13:43Z"
source:
  kind: "conversation"
  ref: "user GitHub branch-protection instruction"
evidence:
  -
    kind: "quote"
    text: "Projects that are on github need to have main branch protection enabled on github, all changes must be made on branches and merged into main via PRs. This should also be part of the instructions"
confirm_public: true
related:
  - "01KTEV4MJRV0XYPQEDN5CN8DVY"
  - "01KTEWPA93PFH1H9ENHV07AVZ5"
content_hash: "sha256:e7b559576350f2c43dcad84039929c47f297253b8fcb7590a4975d1929bf53e9"
---
For Brick-enabled projects hosted on GitHub, packaged agent instructions must require GitHub server-side `main` branch protection. Agents must make tracked-file changes on task branches created from up-to-date `main`, push branches, and merge into `main` only through pull requests. Direct pushes to `main` are not allowed unless the user explicitly overrides the rule for an exceptional situation.
