## Product direction: repo-local project memory system

- The project is for developer teams and open source communities first.
- The product should help contributors clone or fork a repo and get their agents up to speed on upstream project preferences, context, and memory.
- The memory system is per-project and lives inside the project repository as tracked files.
- The canonical memory should be plain-text, human-readable Markdown because it works with Git, forks, branches, PRs, and review.
- Semantic/vector memory is treated as a repo-local or locally rebuilt database/projection, not as the Git source of truth.
- The product promise is a repo-local semantic memory database and memory-management structure for handling memories from forks in a Git-manageable way.
- The system should support upstream maintainers receiving, reviewing, merging, deduplicating, and reconciling memory contributions from forks.
- The first must-win use case is an open source contributor forking a repo, doing work with an agent, recording useful project context discovered during that work, and submitting code plus useful memory back upstream.
- The project should be local-first and free/open source.
- The intended packaging should avoid required installation as much as possible: docs, scripts, agent instructions, and skills live in the repo so a contributor can fork or clone and start working.
- The system should be agent-runtime/framework agnostic and should work through repo scripts plus agent-facing instructions rather than depending on one specific agent platform.
- Agents should not write memories directly. They should route writes, edits, and retrieval through the memory system so consistency checks are enforced.
- Human review should happen mainly through the normal PR process. During local work, agents should confirm what memory will be recorded and clarify/verify with the user when needed.
- One memory atom is one Markdown file containing one piece of a topic.
- The memory taxonomy should adapt the earlier proposed categories and include decisions, preferences, facts/context, incidents, patterns, tasks, people, projects, policies, skills, routines, and commands.
- Duplicate handling should merge exact identical copies and reevaluate semantically similar memories before merging.
- Conflicting memories should go to human review.
- Retrieval should be hybrid rather than semantic-only.
- Reranking is probably not a v1 requirement because it likely requires an additional model and may be too heavy.
- The user is working on a separate system-wide local micro LLM/embedding server, but the memory project should also be able to use API-backed LLMs/embeddings.
- Memory markdown should expose enough citations, source references, confidence, and context for users and agents to decide whether to trust a memory.
- Memory belongs inside each project repo; every repo has its own memory.
- Collaboration should use normal Git workflows: branches, forks, PRs, and merges.
- A custom Markdown/memory merge driver is likely central to the system.
- The project should not rely on product telemetry.
- Debugging should prefer verbose logs.

## Collaboration preference

- The user may be inconsistent while defining the product and does not expect to understand every surrounding technical choice up front.
- When answers are unclear, ask more granular questions or work through them slowly instead of forcing a premature full specification.
- Capture firm answers in `.agents/MEMORIES.md`; after the clarification process is finished, produce a detailed design plan and roadmap.
