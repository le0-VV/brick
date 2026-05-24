from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from brick.memory import MemoryParseError, format_timestamp, generate_ulid, load_memory


CONFLICT_SCHEMA_VERSION = 1
CONFLICTS_RELATIVE_PATH = Path(".agents/brick/conflicts")


class BrickConflictError(RuntimeError):
    pass


@dataclass
class ConflictReportResult:
    report: dict[str, Any]
    path: Path

    def to_dict(self, repo_root: Path) -> dict[str, Any]:
        return {
            "status": "ok",
            "report": self.report,
            "path": relative_to_repo(repo_root, self.path),
        }


@dataclass
class MergeDriverResult:
    status: str
    action: str
    report: ConflictReportResult | None = None

    def to_dict(self, repo_root: Path) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "action": self.action,
        }
        if self.report is not None:
            payload["report_path"] = relative_to_repo(repo_root, self.report.path)
            payload["report_id"] = self.report.report["id"]
        return payload


@dataclass(frozen=True)
class MergeDriverArgs:
    base: Path
    ours: Path
    theirs: Path
    marker_size: str | None = None
    memory_path: str | None = None


def conflicts_dir(repo_root: Path) -> Path:
    return repo_root / CONFLICTS_RELATIVE_PATH


def list_conflict_reports(repo_root: Path) -> dict[str, Any]:
    reports = []
    root = conflicts_dir(repo_root)
    if root.exists():
        for path in sorted(root.glob("*.json")):
            report = read_json_file(path)
            reports.append(conflict_summary(repo_root, path, report))
    reports.sort(key=lambda item: (item.get("created_at") or "", item.get("id") or ""))
    return {
        "status": "ok",
        "count": len(reports),
        "reports": reports,
    }


def export_conflict_report(repo_root: Path, report_id: str) -> dict[str, Any]:
    path = conflict_path_for_id(repo_root, report_id)
    if not path.exists():
        raise BrickConflictError(f"conflict report not found: {report_id}")
    return {
        "status": "ok",
        "path": relative_to_repo(repo_root, path),
        "report": read_json_file(path),
    }


def run_merge_driver(repo_root: Path, raw_args: list[str]) -> MergeDriverResult:
    args = parse_merge_driver_args(raw_args)
    base_text = read_text(args.base)
    ours_text = read_text(args.ours)
    theirs_text = read_text(args.theirs)

    if ours_text == theirs_text:
        args.ours.write_text(ours_text, encoding="utf-8")
        return MergeDriverResult(status="ok", action="identical")
    if base_text == ours_text:
        args.ours.write_text(theirs_text, encoding="utf-8")
        return MergeDriverResult(status="ok", action="use_theirs")
    if base_text == theirs_text:
        args.ours.write_text(ours_text, encoding="utf-8")
        return MergeDriverResult(status="ok", action="keep_ours")
    if same_memory_content(args.ours, args.theirs):
        args.ours.write_text(ours_text, encoding="utf-8")
        return MergeDriverResult(status="ok", action="same_memory_content")

    report = create_merge_conflict_report(repo_root, args)
    return MergeDriverResult(status="conflict", action="human_review", report=report)


def parse_merge_driver_args(raw_args: list[str]) -> MergeDriverArgs:
    if len(raw_args) < 3:
        raise BrickConflictError("merge-driver requires at least base, ours, and theirs paths")
    return MergeDriverArgs(
        base=Path(raw_args[0]),
        ours=Path(raw_args[1]),
        theirs=Path(raw_args[2]),
        marker_size=raw_args[3] if len(raw_args) > 3 else None,
        memory_path=raw_args[4] if len(raw_args) > 4 else None,
    )


def create_merge_conflict_report(repo_root: Path, args: MergeDriverArgs) -> ConflictReportResult:
    conflict_id = f"conflict-{generate_ulid()}"
    report = {
        "schema_version": CONFLICT_SCHEMA_VERSION,
        "id": conflict_id,
        "created_at": format_timestamp(datetime.now(UTC)),
        "kind": "memory_merge_conflict",
        "severity": "review_required",
        "merge": {
            "base_ref": path_ref(args.base),
            "ours_ref": path_ref(args.ours),
            "theirs_ref": path_ref(args.theirs),
            "path": args.memory_path,
        },
        "memories": [
            memory_report_entry(repo_root, "base", args.base),
            memory_report_entry(repo_root, "ours", args.ours),
            memory_report_entry(repo_root, "theirs", args.theirs),
        ],
        "similarity": {
            "method": "not_evaluated",
            "score": None,
        },
        "conflicts": [
            {
                "field": "file",
                "reason": "merge_driver_safe_resolution_not_available",
            }
        ],
        "appendable_unions": {
            "evidence": [],
        },
        "proposed_resolution": None,
        "required_action": "human_review",
    }
    path = write_conflict_report(repo_root, report)
    return ConflictReportResult(report=report, path=path)


def write_conflict_report(repo_root: Path, report: dict[str, Any]) -> Path:
    root = conflicts_dir(repo_root)
    root.mkdir(parents=True, exist_ok=True)
    conflict_id = report.get("id")
    if not isinstance(conflict_id, str) or not conflict_id:
        raise BrickConflictError("conflict report requires a non-empty id")
    path = root / f"{safe_report_id(conflict_id)}.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def conflict_path_for_id(repo_root: Path, report_id: str) -> Path:
    stem = Path(report_id).name
    if stem.endswith(".json"):
        stem = stem[:-5]
    return conflicts_dir(repo_root) / f"{safe_report_id(stem)}.json"


def safe_report_id(report_id: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if not report_id or any(character not in allowed for character in report_id):
        raise BrickConflictError(f"invalid conflict report id: {report_id}")
    return report_id


def conflict_summary(repo_root: Path, path: Path, report: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": report.get("id"),
        "path": relative_to_repo(repo_root, path),
        "created_at": report.get("created_at"),
        "kind": report.get("kind"),
        "severity": report.get("severity"),
        "required_action": report.get("required_action"),
        "memory_count": len(report.get("memories", [])) if isinstance(report.get("memories"), list) else 0,
    }


def read_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BrickConflictError(f"could not read conflict report {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BrickConflictError(f"conflict report must be a JSON object: {path}")
    return payload


def same_memory_content(ours: Path, theirs: Path) -> bool:
    try:
        ours_memory = load_memory(ours)
        theirs_memory = load_memory(theirs)
    except (OSError, UnicodeDecodeError, MemoryParseError):
        return False
    return (
        ours_memory.frontmatter.get("id") == theirs_memory.frontmatter.get("id")
        and ours_memory.frontmatter.get("content_hash") == theirs_memory.frontmatter.get("content_hash")
    )


def memory_report_entry(repo_root: Path, side: str, path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "side": side,
        "path": path_ref(path, repo_root),
    }
    try:
        document = load_memory(path)
    except (OSError, UnicodeDecodeError, MemoryParseError) as exc:
        entry["parse_error"] = str(exc)
        return entry
    frontmatter = document.frontmatter
    for field_name in ("id", "title", "type", "status", "content_hash"):
        if field_name in frontmatter:
            entry[field_name] = frontmatter[field_name]
    return entry


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BrickConflictError(f"could not read merge file {path}: {exc}") from exc


def path_ref(path: Path, repo_root: Path | None = None) -> str:
    if repo_root is not None:
        try:
            return relative_to_repo(repo_root, path)
        except ValueError:
            pass
    return str(path)


def relative_to_repo(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve()))
