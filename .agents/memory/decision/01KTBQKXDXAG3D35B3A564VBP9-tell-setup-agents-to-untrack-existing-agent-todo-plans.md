---
id: "01KTBQKXDXAG3D35B3A564VBP9"
title: "Tell setup agents to untrack existing agent TODO plans"
type: "decision"
status: "active"
tags:
  - "setup"
  - "gitignore"
  - "agents"
  - "todo"
  - "docs"
created_at: "2026-06-05T11:10:12Z"
updated_at: "2026-06-05T11:10:12Z"
source:
  kind: "conversation"
  ref: "user setup-agent untrack instruction"
evidence:
  -
    kind: "quote"
    text: "in setup instructions for agents, tell agents to untrack `.agents/TODO.md` if the file exists"
confirm_public: true
content_hash: "sha256:47e5f5f15e4a8692fbe399fa44717fd5c758361deeb487b1f778238c747a8260"
---
Brick setup instructions for agents should tell agents to untrack `.agents/TODO.md` when the file already exists and is tracked, preserving the local file while removing it from Git tracking.
