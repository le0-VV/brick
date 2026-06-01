---
id: "01KT0WNCMT96A0DGCWMYD34QJ5"
title: "Use root AGENTS.md verbatim as the setup package agent template"
type: "decision"
status: "active"
tags:
  - "agents"
  - "setup"
  - "template"
  - "installer"
created_at: "2026-06-01T06:06:45Z"
updated_at: "2026-06-01T06:06:45Z"
source:
  kind: "conversation"
  ref: "user setup-package instruction"
evidence:
  -
    kind: "quote"
    text: "[AGENTS.md](AGENTS.md) , word for word, is what i want to include in the setup package"
confirm_public: true
content_hash: "sha256:252b20cc29ee899beb4ff0e93c827bdde3333906f9e83f5da43dc9a926349837"
---
Brick setup packaging should use the repository root `AGENTS.md` content word for word as the agent instruction template installed into Brick-enabled repositories.
