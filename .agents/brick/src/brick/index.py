from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from brick.memory import (
    MemoryDocument,
    ValidationResult,
    discover_memory_files,
    format_timestamp,
    load_memory,
    normalize_body,
    validate_memory_paths,
)


INDEX_SCHEMA_VERSION = 1
INDEX_RELATIVE_PATH = Path(".agents/brick/index/brick.sqlite3")
SEMANTIC_ENV_VAR = "BRICK_EMBEDDING_URL"
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
MAX_SUMMARY_LENGTH = 240


class BrickIndexError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "index_error",
        payload: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        if self.payload is not None:
            return self.payload
        return {
            "status": "error",
            "reason": self.code,
            "message": str(self),
        }


@dataclass
class RebuildResult:
    path: Path
    rebuilt_at: str
    memory_count: int
    validation_results: list[ValidationResult]

    def to_dict(self, repo_root: Path) -> dict[str, Any]:
        return {
            "status": "ok",
            "index": {
                "path": relative_to_repo(repo_root, self.path),
                "schema_version": INDEX_SCHEMA_VERSION,
                "rebuilt_at": self.rebuilt_at,
                "memory_count": self.memory_count,
            },
            "checked": len(self.validation_results),
            "results": [result.to_dict(repo_root) for result in self.validation_results],
        }


def index_path(repo_root: Path) -> Path:
    return repo_root / INDEX_RELATIVE_PATH


def rebuild_index(repo_root: Path, *, now: datetime | None = None) -> RebuildResult:
    repo_root = repo_root.resolve()
    paths = discover_memory_files(repo_root)
    validation_results = validate_memory_paths(repo_root, paths)
    validation_status = aggregate_validation_status(validation_results)
    if validation_status != "ok":
        raise BrickIndexError(
            "memory validation failed",
            code="memory_validation_failed",
            payload={
                "status": validation_status,
                "reason": "memory_validation_failed",
                "checked": len(validation_results),
                "results": [result.to_dict(repo_root) for result in validation_results],
            },
        )

    documents = [load_memory(path) for path in paths]
    rebuilt_at = format_timestamp(now or datetime.now(UTC))
    target = index_path(repo_root)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise index_write_error(repo_root, target, exc) from exc
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        if temporary.exists():
            temporary.unlink()
    except OSError as exc:
        raise index_write_error(repo_root, target, exc) from exc

    try:
        connection = sqlite3.connect(temporary)
        try:
            initialize_schema(connection)
            write_metadata(connection, rebuilt_at, len(documents))
            for document in documents:
                insert_memory(connection, repo_root, document)
            connection.commit()
        finally:
            connection.close()
        os.replace(temporary, target)
    except sqlite3.Error as exc:
        raise index_write_error(repo_root, target, exc) from exc
    except OSError as exc:
        raise index_write_error(repo_root, target, exc) from exc
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass

    return RebuildResult(
        path=target,
        rebuilt_at=rebuilt_at,
        memory_count=len(documents),
        validation_results=validation_results,
    )


def aggregate_validation_status(results: list[ValidationResult]) -> str:
    if any(result.status == "blocked" for result in results):
        return "blocked"
    if any(result.status == "invalid" for result in results):
        return "invalid"
    return "ok"


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.execute(f"PRAGMA user_version = {INDEX_SCHEMA_VERSION}")
    connection.execute(
        """
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE memories (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            source_json TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            summary TEXT NOT NULL,
            body TEXT NOT NULL,
            search_text TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX memories_status_idx ON memories(status)")
    connection.execute("CREATE INDEX memories_type_idx ON memories(type)")


def write_metadata(connection: sqlite3.Connection, rebuilt_at: str, memory_count: int) -> None:
    rows = {
        "schema_version": str(INDEX_SCHEMA_VERSION),
        "rebuilt_at": rebuilt_at,
        "memory_count": str(memory_count),
    }
    connection.executemany(
        "INSERT INTO metadata (key, value) VALUES (?, ?)",
        sorted(rows.items()),
    )


def insert_memory(connection: sqlite3.Connection, repo_root: Path, document: MemoryDocument) -> None:
    frontmatter = document.frontmatter
    title = as_text(frontmatter["title"])
    body = normalize_body(document.body)
    summary = summarize_body(body, title)
    tags = frontmatter["tags"]
    source = frontmatter["source"]
    evidence = frontmatter["evidence"]
    row = {
        "id": as_text(frontmatter["id"]),
        "path": relative_to_repo(repo_root, document.path),
        "title": title,
        "type": as_text(frontmatter["type"]),
        "status": as_text(frontmatter["status"]),
        "tags_json": json_dumps(tags),
        "source_json": json_dumps(source),
        "evidence_json": json_dumps(evidence),
        "content_hash": as_text(frontmatter["content_hash"]),
        "summary": summary,
        "body": body,
        "search_text": build_search_text(frontmatter, body, summary),
        "updated_at": as_text(frontmatter["updated_at"]),
    }
    connection.execute(
        """
        INSERT INTO memories (
            id, path, title, type, status, tags_json, source_json, evidence_json,
            content_hash, summary, body, search_text, updated_at
        )
        VALUES (
            :id, :path, :title, :type, :status, :tags_json, :source_json,
            :evidence_json, :content_hash, :summary, :body, :search_text,
            :updated_at
        )
        """,
        row,
    )


def search_index(
    repo_root: Path,
    query: str,
    *,
    limit: int = 10,
    include_superseded: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    if limit <= 0:
        raise BrickIndexError(
            "limit must be greater than zero",
            code="invalid_limit",
            payload={
                "status": "invalid",
                "reason": "invalid_limit",
                "message": "limit must be greater than zero",
            },
        )
    terms = unique_terms(query)
    if not terms:
        raise BrickIndexError(
            "query must contain at least one searchable term",
            code="invalid_query",
            payload={
                "status": "invalid",
                "reason": "invalid_query",
                "message": "query must contain at least one searchable term",
            },
        )

    target = index_path(repo_root)
    if not target.exists():
        raise BrickIndexError(
            "Brick index has not been built",
            code="index_missing",
            payload={
                "status": "error",
                "reason": "index_missing",
                "message": "Brick index has not been built. Run `brick rebuild` first.",
                "action": "run brick rebuild",
            },
        )

    try:
        connection = sqlite3.connect(target)
    except sqlite3.Error as exc:
        raise index_read_error(repo_root, target, exc) from exc
    try:
        connection.row_factory = sqlite3.Row
        metadata = read_metadata(connection)
        rows = read_search_rows(connection, include_superseded=include_superseded)
    except sqlite3.Error as exc:
        raise index_read_error(repo_root, target, exc) from exc
    finally:
        connection.close()

    scored = []
    for row in rows:
        score, matched_terms = score_row(row, query, terms)
        if score <= 0:
            continue
        scored.append((score, row["path"], matched_terms, row))
    scored.sort(key=lambda item: (-item[0], item[1]))
    limited = scored[:limit]

    return {
        "status": "ok",
        "query": query,
        "index": {
            "path": relative_to_repo(repo_root, target),
            "schema_version": metadata.get("schema_version", INDEX_SCHEMA_VERSION),
            "rebuilt_at": metadata.get("rebuilt_at"),
            "memory_count": metadata.get("memory_count", 0),
        },
        "retrieval": {
            "mode": "keyword",
            "semantic": semantic_status(env or os.environ),
        },
        "filters": {
            "include_superseded": include_superseded,
            "statuses": ["active", "superseded"] if include_superseded else ["active"],
        },
        "results": [
            result_from_row(repo_root, row, score, matched_terms)
            for score, _path, matched_terms, row in limited
        ],
    }


def read_metadata(connection: sqlite3.Connection) -> dict[str, Any]:
    rows = connection.execute("SELECT key, value FROM metadata").fetchall()
    metadata: dict[str, Any] = {}
    for key, value in rows:
        if key in {"schema_version", "memory_count"}:
            metadata[key] = int(value)
        else:
            metadata[key] = value
    return metadata


def read_search_rows(
    connection: sqlite3.Connection,
    *,
    include_superseded: bool,
) -> list[sqlite3.Row]:
    statuses = ("active", "superseded") if include_superseded else ("active",)
    placeholders = ", ".join("?" for _ in statuses)
    return connection.execute(
        f"""
        SELECT
            id, path, title, type, status, tags_json, source_json, evidence_json,
            content_hash, summary, body, search_text, updated_at
        FROM memories
        WHERE status IN ({placeholders})
        ORDER BY path
        """,
        statuses,
    ).fetchall()


def score_row(row: sqlite3.Row, query: str, terms: list[str]) -> tuple[int, list[str]]:
    tags = json.loads(row["tags_json"])
    source = json.loads(row["source_json"])
    evidence = json.loads(row["evidence_json"])
    fields = (
        (row["title"], 8, 12),
        (" ".join(tags), 6, 10),
        (row["type"], 4, 0),
        (json_dumps(evidence), 3, 5),
        (row["summary"], 3, 6),
        (json_dumps(source), 2, 3),
        (row["body"], 1, 4),
    )
    phrase = normalize_search_text(query)
    score = 0
    matched: set[str] = set()
    for text, term_weight, phrase_weight in fields:
        tokens = tokenize(text)
        token_counts = {term: tokens.count(term) for term in terms}
        for term, count in token_counts.items():
            if count:
                score += term_weight * count
                matched.add(term)
        if phrase and phrase_weight and phrase in normalize_search_text(text):
            score += phrase_weight
    return score, [term for term in terms if term in matched]


def result_from_row(
    repo_root: Path,
    row: sqlite3.Row,
    score: int,
    matched_terms: list[str],
) -> dict[str, Any]:
    source_path = row["path"]
    return {
        "id": row["id"],
        "title": row["title"],
        "type": row["type"],
        "status": row["status"],
        "tags": json.loads(row["tags_json"]),
        "source_path": source_path,
        "full_text_path": source_path,
        "source": json.loads(row["source_json"]),
        "evidence": json.loads(row["evidence_json"]),
        "summary": row["summary"],
        "content_hash": row["content_hash"],
        "score": score,
        "confidence": confidence_for_score(score),
        "matched_terms": matched_terms,
    }


def semantic_status(env: Mapping[str, str]) -> dict[str, Any]:
    configured = bool(env.get(SEMANTIC_ENV_VAR, "").strip())
    if not configured:
        return {
            "available": False,
            "reason": f"{SEMANTIC_ENV_VAR}_not_configured",
            "env": SEMANTIC_ENV_VAR,
        }
    return {
        "available": False,
        "reason": "embedding_endpoint_not_implemented",
        "env": SEMANTIC_ENV_VAR,
        "url_configured": True,
    }


def index_write_error(repo_root: Path, target: Path, exc: BaseException) -> BrickIndexError:
    return BrickIndexError(
        f"could not write Brick index: {exc}",
        code="index_write_failed",
        payload={
            "status": "error",
            "reason": "index_write_failed",
            "path": relative_to_repo(repo_root, target),
            "message": str(exc),
        },
    )


def index_read_error(repo_root: Path, target: Path, exc: BaseException) -> BrickIndexError:
    return BrickIndexError(
        f"could not read Brick index: {exc}",
        code="index_read_failed",
        payload={
            "status": "error",
            "reason": "index_read_failed",
            "path": relative_to_repo(repo_root, target),
            "message": str(exc),
        },
    )


def build_search_text(frontmatter: dict[str, Any], body: str, summary: str) -> str:
    parts = [
        as_text(frontmatter.get("title", "")),
        as_text(frontmatter.get("type", "")),
        " ".join(frontmatter.get("tags", [])),
        json_dumps(frontmatter.get("source", {})),
        json_dumps(frontmatter.get("evidence", [])),
        summary,
        body,
    ]
    return normalize_search_text(" ".join(parts))


def summarize_body(body: str, fallback_title: str) -> str:
    collapsed = re.sub(r"\s+", " ", normalize_body(body)).strip()
    if not collapsed:
        return fallback_title
    if len(collapsed) <= MAX_SUMMARY_LENGTH:
        return collapsed
    return collapsed[: MAX_SUMMARY_LENGTH - 3].rstrip() + "..."


def confidence_for_score(score: int) -> str:
    if score >= 20:
        return "high"
    if score >= 8:
        return "medium"
    return "low"


def unique_terms(query: str) -> list[str]:
    return list(dict.fromkeys(tokenize(query)))


def tokenize(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower())


def normalize_search_text(value: str) -> str:
    return " ".join(tokenize(value))


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def as_text(value: Any) -> str:
    return str(value)


def relative_to_repo(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve()))
