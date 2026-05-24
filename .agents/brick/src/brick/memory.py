from __future__ import annotations

import hashlib
import json
import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ALLOWED_TYPES = {
    "decision",
    "command",
    "routine",
    "skill",
    "preference",
    "fact",
    "incident",
    "pattern",
    "task",
    "policy",
}
ALLOWED_STATUSES = {"active", "superseded", "tombstone", "redacted"}
REQUIRED_FIELDS = {
    "id",
    "title",
    "type",
    "status",
    "tags",
    "created_at",
    "updated_at",
    "content_hash",
    "source",
    "evidence",
}
ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")
CONTENT_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "credential_assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|token|secret|password)"
            r"\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"
        ),
    ),
)
PII_PATTERNS = (
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"\b(?:\+?\d[\d ()-]{7,}\d)\b")),
    (
        "address",
        re.compile(
            r"\b\d{1,6}\s+[A-Z][A-Za-z0-9.-]*"
            r"(?:\s+[A-Z][A-Za-z0-9.-]*){0,4}\s+"
            r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b"
        ),
    ),
    (
        "person_name",
        re.compile(
            r"(?i)\b(?:name|user|author|maintainer|contributor|person)\s*[:=]\s*"
            r"([A-Z][a-z]{1,}\s+[A-Z][a-z]{1,})\b"
        ),
    ),
)


class MemoryParseError(ValueError):
    pass


@dataclass
class MemoryDocument:
    path: Path
    frontmatter: dict[str, Any]
    body: str
    raw_text: str


@dataclass
class ValidationIssue:
    code: str
    message: str
    field: str | None = None
    line: int | None = None
    kind: str | None = None
    expected: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.field is not None:
            payload["field"] = self.field
        if self.line is not None:
            payload["line"] = self.line
        if self.kind is not None:
            payload["kind"] = self.kind
            payload["text"] = "[REDACTED]"
        if self.expected is not None:
            payload["expected"] = self.expected
        return payload


@dataclass
class ValidationResult:
    path: Path
    issues: list[ValidationIssue] = field(default_factory=list)
    expected_content_hash: str | None = None

    @property
    def status(self) -> str:
        if not self.issues:
            return "ok"
        if any(issue.code in {"secret_detected", "possible_pii"} for issue in self.issues):
            return "blocked"
        return "invalid"

    def to_dict(self, repo_root: Path | None = None) -> dict[str, Any]:
        path = self.path
        if repo_root is not None:
            try:
                path_text = str(path.resolve().relative_to(repo_root.resolve()))
            except ValueError:
                path_text = str(path)
        else:
            path_text = str(path)
        payload: dict[str, Any] = {
            "path": path_text,
            "status": self.status,
            "issues": [issue.to_dict() for issue in self.issues],
        }
        if self.expected_content_hash is not None:
            payload["expected_content_hash"] = self.expected_content_hash
        return payload


def split_frontmatter(text: str) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        raise MemoryParseError("memory file must start with YAML frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index] == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    raise MemoryParseError("memory file is missing closing YAML frontmatter delimiter")


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    raw_lines = frontmatter.split("\n")
    lines: list[tuple[int, str, int]] = []
    for line_number, raw in enumerate(raw_lines, start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise MemoryParseError(f"tabs are not supported in frontmatter at line {line_number}")
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip(), line_number))
    if not lines:
        return {}
    parsed, next_index = parse_block(lines, 0, lines[0][0])
    if next_index != len(lines):
        raise MemoryParseError(f"unexpected frontmatter content at line {lines[next_index][2]}")
    if not isinstance(parsed, dict):
        raise MemoryParseError("frontmatter root must be a mapping")
    return parsed


def parse_block(
    lines: list[tuple[int, str, int]],
    index: int,
    indent: int,
) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    current_indent, content, _line_number = lines[index]
    if current_indent < indent:
        return {}, index
    if current_indent > indent:
        raise MemoryParseError(f"unexpected indentation at line {lines[index][2]}")
    if content == "-" or content.startswith("- "):
        return parse_list(lines, index, indent)
    return parse_mapping(lines, index, indent)


def parse_mapping(
    lines: list[tuple[int, str, int]],
    index: int,
    indent: int,
) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        current_indent, content, line_number = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise MemoryParseError(f"unexpected indentation at line {line_number}")
        if content == "-" or content.startswith("- "):
            break
        key, value_text = split_key_value(content, line_number)
        if key in mapping:
            raise MemoryParseError(f"duplicate key {key!r} at line {line_number}")
        index += 1
        if value_text == "":
            if index < len(lines) and lines[index][0] > current_indent:
                value, index = parse_block(lines, index, lines[index][0])
            else:
                value = {}
        else:
            value = parse_scalar(value_text, line_number)
        mapping[key] = value
    return mapping, index


def parse_list(
    lines: list[tuple[int, str, int]],
    index: int,
    indent: int,
) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        current_indent, content, line_number = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise MemoryParseError(f"unexpected indentation at line {line_number}")
        if content != "-" and not content.startswith("- "):
            break
        item_text = "" if content == "-" else content[2:].strip()
        index += 1
        if item_text == "":
            if index < len(lines) and lines[index][0] > current_indent:
                item, index = parse_block(lines, index, lines[index][0])
            else:
                item = None
        elif ":" in item_text and not is_quoted(item_text):
            key, value_text = split_key_value(item_text, line_number)
            item = {key: parse_scalar(value_text, line_number) if value_text else {}}
            if index < len(lines) and lines[index][0] > current_indent:
                extra, index = parse_block(lines, index, lines[index][0])
                if isinstance(extra, dict):
                    item.update(extra)
                else:
                    raise MemoryParseError(f"list item mapping expected at line {line_number}")
        else:
            item = parse_scalar(item_text, line_number)
        items.append(item)
    return items, index


def split_key_value(content: str, line_number: int) -> tuple[str, str]:
    if ":" not in content:
        raise MemoryParseError(f"expected key/value pair at line {line_number}")
    key, value = content.split(":", 1)
    key = key.strip()
    if not key:
        raise MemoryParseError(f"empty key at line {line_number}")
    return key, value.strip()


def parse_scalar(value: str, line_number: int) -> Any:
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip(), line_number) for part in inner.split(",")]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if is_quoted(value):
        quote = value[0]
        body = value[1:-1]
        if quote == '"':
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise MemoryParseError(f"invalid quoted string at line {line_number}") from exc
        return body.replace("''", "'")
    return value


def is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}


def load_memory(path: Path) -> MemoryDocument:
    raw_text = path.read_text(encoding="utf-8")
    frontmatter_text, body = split_frontmatter(raw_text)
    frontmatter = parse_frontmatter(frontmatter_text)
    return MemoryDocument(path=path, frontmatter=frontmatter, body=body, raw_text=raw_text)


def normalize_body(body: str) -> str:
    lines = body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = "\n".join(line.rstrip() for line in lines).rstrip()
    return f"{normalized}\n" if normalized else ""


def canonical_frontmatter(frontmatter: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in frontmatter.items()
        if key not in {"content_hash", "updated_at"}
    }


def compute_content_hash(frontmatter: dict[str, Any], body: str) -> str:
    payload = {
        "frontmatter": canonical_frontmatter(frontmatter),
        "body": normalize_body(body),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_memory(document: MemoryDocument) -> ValidationResult:
    result = ValidationResult(path=document.path)
    frontmatter = document.frontmatter

    for field_name in sorted(REQUIRED_FIELDS):
        if field_name not in frontmatter:
            result.issues.append(
                ValidationIssue(
                    code="missing_required_field",
                    message=f"missing required field {field_name}",
                    field=field_name,
                )
            )

    validate_scalar_string(result, frontmatter, "id")
    if isinstance(frontmatter.get("id"), str) and not ULID_RE.fullmatch(frontmatter["id"]):
        result.issues.append(
            ValidationIssue(code="invalid_ulid", message="id must be a plain uppercase ULID", field="id")
        )

    validate_scalar_string(result, frontmatter, "title")
    validate_scalar_string(result, frontmatter, "type")
    if isinstance(frontmatter.get("type"), str) and frontmatter["type"] not in ALLOWED_TYPES:
        result.issues.append(
            ValidationIssue(code="invalid_type", message="type is not allowed", field="type")
        )

    validate_scalar_string(result, frontmatter, "status")
    if isinstance(frontmatter.get("status"), str) and frontmatter["status"] not in ALLOWED_STATUSES:
        result.issues.append(
            ValidationIssue(code="invalid_status", message="status is not allowed", field="status")
        )
    validate_durable_confidence(result, frontmatter)

    validate_string_list(result, frontmatter, "tags")
    validate_timestamp(result, frontmatter, "created_at")
    validate_timestamp(result, frontmatter, "updated_at")
    validate_content_hash(result, document)
    validate_source(result, frontmatter)
    validate_evidence(result, frontmatter)
    validate_ulid_list(result, frontmatter, "supersedes")
    validate_ulid_list(result, frontmatter, "related")
    scan_safety(result, document)
    return result


def validate_scalar_string(
    result: ValidationResult,
    frontmatter: dict[str, Any],
    field_name: str,
) -> None:
    if field_name in frontmatter and not isinstance(frontmatter[field_name], str):
        result.issues.append(
            ValidationIssue(
                code="invalid_field_type",
                message=f"{field_name} must be a string",
                field=field_name,
            )
        )


def validate_string_list(
    result: ValidationResult,
    frontmatter: dict[str, Any],
    field_name: str,
) -> None:
    if field_name not in frontmatter:
        return
    value = frontmatter[field_name]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        result.issues.append(
            ValidationIssue(
                code="invalid_field_type",
                message=f"{field_name} must be a list of strings",
                field=field_name,
            )
        )


def validate_timestamp(
    result: ValidationResult,
    frontmatter: dict[str, Any],
    field_name: str,
) -> None:
    if field_name not in frontmatter or not isinstance(frontmatter[field_name], str):
        return
    value = frontmatter[field_name]
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        result.issues.append(
            ValidationIssue(
                code="invalid_timestamp",
                message=f"{field_name} must be an ISO 8601 timestamp",
                field=field_name,
            )
        )


def validate_durable_confidence(result: ValidationResult, frontmatter: dict[str, Any]) -> None:
    confidence = frontmatter.get("confidence")
    if not isinstance(confidence, str):
        return
    if confidence.lower() in {"low", "medium", "uncertain", "unverified", "unsupported"}:
        result.issues.append(
            ValidationIssue(
                code="unsupported_durable_memory",
                message="low-confidence memory must be clarified or rejected before it is durable",
                field="confidence",
            )
        )


def validate_content_hash(result: ValidationResult, document: MemoryDocument) -> None:
    value = document.frontmatter.get("content_hash")
    if not isinstance(value, str):
        return
    expected = compute_content_hash(document.frontmatter, document.body)
    result.expected_content_hash = expected
    if not CONTENT_HASH_RE.fullmatch(value):
        result.issues.append(
            ValidationIssue(
                code="invalid_content_hash",
                message="content_hash must be sha256:<64 lowercase hex characters>",
                field="content_hash",
                expected=expected,
            )
        )
    elif value != expected:
        result.issues.append(
            ValidationIssue(
                code="content_hash_mismatch",
                message="content_hash does not match normalized memory content",
                field="content_hash",
                expected=expected,
            )
        )


def validate_source(result: ValidationResult, frontmatter: dict[str, Any]) -> None:
    source = frontmatter.get("source")
    if source is None:
        return
    if not isinstance(source, dict):
        result.issues.append(
            ValidationIssue(code="invalid_field_type", message="source must be a mapping", field="source")
        )
        return
    kind = source.get("kind")
    if not isinstance(kind, str) or not kind:
        result.issues.append(
            ValidationIssue(
                code="missing_required_field",
                message="source.kind is required",
                field="source.kind",
            )
        )


def validate_evidence(result: ValidationResult, frontmatter: dict[str, Any]) -> None:
    evidence = frontmatter.get("evidence")
    if evidence is None:
        return
    if not isinstance(evidence, list) or not evidence:
        result.issues.append(
            ValidationIssue(
                code="missing_evidence",
                message="evidence must contain at least one item",
                field="evidence",
            )
        )
        return
    for item in evidence:
        if isinstance(item, str) and item.strip():
            continue
        if isinstance(item, dict) and any(str(value).strip() for value in item.values()):
            continue
        result.issues.append(
            ValidationIssue(
                code="missing_evidence",
                message="evidence items must be non-empty strings or mappings",
                field="evidence",
            )
        )
        break


def validate_ulid_list(
    result: ValidationResult,
    frontmatter: dict[str, Any],
    field_name: str,
) -> None:
    if field_name not in frontmatter:
        return
    value = frontmatter[field_name]
    if not isinstance(value, list):
        result.issues.append(
            ValidationIssue(
                code="invalid_field_type",
                message=f"{field_name} must be a list of ULIDs",
                field=field_name,
            )
        )
        return
    for item in value:
        if not isinstance(item, str) or not ULID_RE.fullmatch(item):
            result.issues.append(
                ValidationIssue(
                    code="invalid_ulid",
                    message=f"{field_name} entries must be plain uppercase ULIDs",
                    field=field_name,
                )
            )
            return


def scan_safety(result: ValidationResult, document: MemoryDocument) -> None:
    scan_text = "\n".join(iter_safety_strings(document))
    for kind, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(scan_text):
            result.issues.append(
                ValidationIssue(
                    code="secret_detected",
                    message=f"blocked likely secret: {kind}",
                    kind=kind,
                    line=line_number_for_match(document.raw_text, match.group(0)),
                )
            )
    if document.frontmatter.get("confirm_public") is True:
        return
    for kind, pattern in PII_PATTERNS:
        for match in pattern.finditer(scan_text):
            result.issues.append(
                ValidationIssue(
                    code="possible_pii",
                    message=f"blocked possible PII: {kind}",
                    kind=kind,
                    line=line_number_for_match(document.raw_text, match.group(0)),
                )
            )


def iter_safety_strings(document: MemoryDocument) -> Iterable[str]:
    yield document.body
    yield from iter_frontmatter_safety_strings(document.frontmatter)


def iter_frontmatter_safety_strings(value: Any, key: str | None = None) -> Iterable[str]:
    skipped_keys = {
        "id",
        "type",
        "status",
        "tags",
        "created_at",
        "updated_at",
        "content_hash",
        "supersedes",
        "related",
        "confirm_public",
    }
    if key in skipped_keys:
        return
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_frontmatter_safety_strings(item)
    elif isinstance(value, dict):
        for child_key, child_value in value.items():
            yield from iter_frontmatter_safety_strings(child_value, child_key)


def line_number_for_match(text: str, matched_text: str) -> int | None:
    offset = text.find(matched_text)
    if offset < 0:
        return None
    return text.count("\n", 0, offset) + 1


def validate_memory_file(path: Path) -> ValidationResult:
    try:
        document = load_memory(path)
    except (OSError, UnicodeDecodeError, MemoryParseError) as exc:
        return ValidationResult(
            path=path,
            issues=[
                ValidationIssue(
                    code="parse_error",
                    message=str(exc),
                )
            ],
        )
    return validate_memory(document)


def discover_memory_files(repo_root: Path, path_arg: str | None = None) -> list[Path]:
    if path_arg is None:
        root = repo_root / ".agents/memory"
        if not root.exists():
            return []
        return sorted(path for path in root.rglob("*.md") if path.is_file())

    path = Path(path_arg)
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(candidate for candidate in path.rglob("*.md") if candidate.is_file())
    raise MemoryParseError(f"validation path does not exist: {path}")


def validate_memory_paths(repo_root: Path, paths: Iterable[Path]) -> list[ValidationResult]:
    return [validate_memory_file(path) for path in paths]


def generate_ulid(timestamp_ms: int | None = None) -> str:
    timestamp = int(time.time() * 1000) if timestamp_ms is None else timestamp_ms
    if timestamp < 0 or timestamp >= 2**48:
        raise ValueError("ULID timestamp must fit in 48 bits")
    value = (timestamp << 80) | secrets.randbits(80)
    return encode_crockford_base32(value, 26)


def encode_crockford_base32(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        chars.append(CROCKFORD_BASE32[value & 0b11111])
        value >>= 5
    if value:
        raise ValueError("value does not fit in requested Crockford base32 length")
    return "".join(reversed(chars))
