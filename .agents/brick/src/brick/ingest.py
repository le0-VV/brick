from __future__ import annotations

from pathlib import Path
from typing import Any

from brick.memory import (
    MemoryAddError,
    MemoryDocument,
    ValidationIssue,
    build_memory_frontmatter,
    forbidden_approval_issues,
    render_memory_text,
    validate_memory,
)


SOURCE_KINDS = {
    "conversation", "work_summary", "file", "commit", "pull_request", "issue", "manual",
}


def invalid_ingest(message: str, field: str) -> None:
    raise MemoryAddError(
        "invalid ingest decision",
        code="invalid_ingest",
        issues=[ValidationIssue(code="invalid_ingest", message=message, field=field)],
    )


def exact_fields(value: Any, required: set[str], field: str) -> None:
    if not isinstance(value, dict) or set(value) != required:
        invalid_ingest("must be an object with exactly these fields: " + ", ".join(sorted(required)), field)


def nonempty_text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        invalid_ingest("must be a non-empty string", field)


def review_memory_ingest(envelope: Any, source_text: str) -> dict[str, Any]:
    """Check an untrusted decision without writing; quoted evidence still needs semantic review."""
    issues = forbidden_approval_issues(envelope)
    if issues:
        raise MemoryAddError("ingest JSON cannot supply approval", issues=issues)
    exact_fields(envelope, {"action", "reason", "questions", "candidate"}, "decision")
    if not isinstance(source_text, str):
        invalid_ingest("source text must be a string supplied separately", "source_text")
    action = envelope["action"]
    if not isinstance(action, str) or action not in {"add", "clarify", "reject"}:
        invalid_ingest("action must be add, clarify or reject", "action")
    nonempty_text(envelope["reason"], "reason")
    questions = envelope["questions"]
    if not isinstance(questions, list) or len(questions) > 3:
        invalid_ingest("questions must contain at most three non-empty strings", "questions")
    for index, question in enumerate(questions):
        nonempty_text(question, f"questions[{index}]")
    candidate = envelope["candidate"]
    if action == "clarify":
        if candidate is not None or not questions:
            invalid_ingest("clarify requires a null candidate and at least one question", "candidate")
    elif action == "reject":
        if candidate is not None or questions:
            invalid_ingest("reject requires a null candidate and no questions", "candidate")
    else:
        if questions:
            invalid_ingest("add must not include questions", "questions")
        exact_fields(candidate, {"title", "type", "tags", "body", "source", "evidence"}, "candidate")
        nonempty_text(candidate["title"], "candidate.title")
        nonempty_text(candidate["body"], "candidate.body")
        tags = candidate["tags"]
        if not isinstance(tags, list) or not 1 <= len(tags) <= 8:
            invalid_ingest("tags must contain one to eight non-empty strings", "candidate.tags")
        for index, tag in enumerate(tags):
            nonempty_text(tag, f"candidate.tags[{index}]")
        source = candidate["source"]
        exact_fields(source, {"kind", "ref"}, "candidate.source")
        nonempty_text(source["kind"], "candidate.source.kind")
        if source["kind"] not in SOURCE_KINDS:
            invalid_ingest("source kind is not allowed", "candidate.source.kind")
        nonempty_text(source["ref"], "candidate.source.ref")
        evidence = candidate["evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 5:
            invalid_ingest("evidence must contain one to five exact source quotes", "candidate.evidence")
        for index, item in enumerate(evidence):
            field = f"candidate.evidence[{index}]"
            exact_fields(item, {"kind", "text"}, field)
            if item["kind"] != "quote":
                invalid_ingest("evidence kind must be quote", f"{field}.kind")
            nonempty_text(item["text"], f"{field}.text")
            if item["text"] not in source_text:
                invalid_ingest("evidence text is not an exact quote from the supplied source", f"{field}.text")
        frontmatter, body = build_memory_frontmatter(candidate)
        document = MemoryDocument(
            path=Path("<review-candidate>"),
            frontmatter=frontmatter,
            body=body,
            raw_text=render_memory_text(frontmatter, body),
        )
        validation = validate_memory(document)
        if validation.status != "ok":
            raise MemoryAddError(
                "ingest candidate did not pass validation",
                code=validation.status,
                issues=validation.issues,
            )
    return {"status": "ok", "decision": envelope, "requires_agent_review": True}
