---
id: "01KTEV4MJRV0XYPQEDN5CN8DVY"
title: "Require signed-commit checks, CI, and protected-main workflows in agent instructions"
type: "policy"
status: "active"
tags:
  - "agents"
  - "git"
  - "ci"
  - "branch-protection"
  - "signatures"
  - "setup"
created_at: "2026-06-06T16:09:29Z"
updated_at: "2026-06-06T16:09:29Z"
source:
  kind: "conversation"
  ref: "user governance improvements from cbonsai-saver"
evidence:
  -
    kind: "quote"
    text: "if host machine's git has configured verified signature for commits, all commit signature must be checked before pushing any commits."
  -
    kind: "quote"
    text: "CI's must be written for all projects. Git-hooked CI scripts for local-only repos and proper GitHub actions (or other cloud solutions) CI properly configured for cloud projects."
  -
    kind: "quote"
    text: "No commits can be pushed directly to Main. All code edits must be made from branches forked from up-to-date Main with proper names, edited and PR'd into main."
  -
    kind: "file_excerpt"
    path: "/Users/leonardw/Projects/cbonsai-saver/AGENTS.md"
    text: "For tracked-file changes, work on a task branch created from up-to-date `main`; use the `codex/` branch prefix unless the user explicitly requests a different branch name or an existing ref conflict makes that prefix impossible."
  -
    kind: "file_excerpt"
    path: "/Users/leonardw/Projects/cbonsai-saver/AGENTS.md"
    text: "All commits and release tags must be signed. Verify the latest commit with `git log -1 --show-signature` before pushing."
content_hash: "sha256:2b923cfa0f708b24f623778373c7779ff6e7ef962dd34031b24dcb456df4fe28"
---
Brick's packaged agent instructions should require three governance rules. First, when the host Git config indicates signed commits or tags are configured, agents must create signed commits and tags, then verify the outgoing commit signatures before pushing. Second, every project should have CI: local-only repositories should use local git-hooked CI scripts, while cloud-backed projects should use proper cloud CI such as GitHub Actions or the equivalent for the hosting platform. Third, tracked-file edits should happen on focused task branches created from up-to-date main; agents must not push directly to main, should integrate through pull requests where available, and should preserve or configure server-side main branch protection where applicable.
