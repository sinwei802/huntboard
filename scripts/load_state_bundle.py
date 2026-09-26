#!/usr/bin/env python3
"""Load and validate a pentest state bundle without reading evidence bodies.

Used by huntboard (and compatible with the shared ./pentest-state/ schema).
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


CORE_FILES = (
    "session-index.json",
    "asset-graph.md",
    "route-stack.md",
    "loot-tracker.md",
    "evidence-index.json",
)
OPTIONAL_FILES = ("hunt-plan.md",)
_SCRIPTS_DIR = Path(__file__).resolve().parent
MARKDOWN_HEADINGS = {
    "asset-graph.md": "# Asset Graph",
    "route-stack.md": "# Route Stack",
    "loot-tracker.md": "# Loot Tracker",
}
TABLE_ID_RE = re.compile(r"^\|\s*([ARHL]-\d+)\s*\|", re.MULTILINE)
ACTIVE_HYPOTHESIS_ID_RE = re.compile(
    r"^\s*\d+\.\s+\*\*\[(H-\d+)\]", re.MULTILINE
)
EVIDENCE_ID_RE = re.compile(r"^E-\d+$")
MARKDOWN_META_RE = re.compile(
    r"^<!-- huntboard-state: (?P<meta>\{.*\}) -->$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RELATIONS = {"supports", "refutes"}
CONFIDENCE = {"high", "medium", "low"}
FRESHNESS = {"stable", "time-bound", "session-bound", "unknown"}
AVAILABILITY = {"saved", "not-saved", "missing"}


@dataclass
class BundleResult:
    root: Path
    status: int
    loaded: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return {0: "complete", 1: "degraded", 2: "unavailable"}[self.status]

    def render(self, full: bool = False) -> str:
        lines = [
            (
                "STATE_BUNDLE "
                f"status={self.label} loaded="
                f"{sum(1 for name in CORE_FILES if name in self.loaded)}/{len(CORE_FILES)} "
                f"root={self.root}"
            )
        ]
        lines.extend(f"ERROR: {item}" for item in self.errors)
        lines.extend(f"WARNING: {item}" for item in self.warnings)
        if not full:
            lines.append("mode=brief (pass --full to dump core file bodies)")
            session_text = self.loaded.get("session-index.json")
            if session_text:
                try:
                    session = json.loads(session_text)
                    lines.append(
                        "session "
                        f"mode={session.get('mode')} "
                        f"scope={session.get('scope')} "
                        f"last_stop={session.get('last_stop')}"
                    )
                except json.JSONDecodeError:
                    lines.append(
                        f"CORE session-index.json: {len(session_text)} bytes (unparsed)"
                    )
            for name in CORE_FILES:
                if name not in self.loaded:
                    continue
                if name == "session-index.json":
                    continue
                lines.append(
                    f"CORE {name}: {len(self.loaded[name])} bytes (not dumped)"
                )
        else:
            for name in CORE_FILES:
                if name not in self.loaded:
                    continue
                lines.append(f"===== BEGIN CORE FILE: {name} =====")
                lines.append(self.loaded[name].rstrip("\n"))
                lines.append(f"===== END CORE FILE: {name} =====")
        for name in OPTIONAL_FILES:
            if name not in self.loaded:
                continue
            body = self.loaded[name]
            if full or name != "hunt-plan.md":
                lines.append(f"===== BEGIN OVERLAY FILE: {name} =====")
                lines.append(body.rstrip("\n"))
                lines.append(f"===== END OVERLAY FILE: {name} =====")
            else:
                lines.extend(_brief_hunt_plan_lines(body))
        return "\n".join(lines) + "\n"


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _iso_with_timezone(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validate_bundle_meta(
    name: str,
    meta: Any,
    errors: list[str],
    warnings: list[str],
) -> tuple[int | None, str | None, str | None]:
    if not isinstance(meta, dict):
        warnings.append(f"{name}: missing v2 bundle metadata (legacy or invalid)")
        return None, None, None

    schema = meta.get("schema_version")
    checkpoint = meta.get("checkpoint_id")
    updated = meta.get("last_updated")
    if schema != 2:
        warnings.append(f"{name}: schema_version is not 2")
    if not isinstance(checkpoint, str) or not checkpoint.strip():
        warnings.append(f"{name}: checkpoint_id is missing")
        checkpoint = None
    if not _iso_with_timezone(updated):
        errors.append(f"{name}: last_updated must be ISO 8601 with timezone")
        updated = None
    return schema if isinstance(schema, int) else None, checkpoint, updated


def _read_core_files(root: Path, result: BundleResult) -> None:
    for name in CORE_FILES:
        candidate = root / name
        if not candidate.exists():
            result.warnings.append(f"{name}: missing")
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            result.errors.append(f"{name}: cannot resolve: {exc}")
            continue
        if not _is_within(resolved, root):
            result.errors.append(f"{name}: symlink escapes state root")
            continue
        if not resolved.is_file():
            result.errors.append(f"{name}: expected a regular file")
            continue
        try:
            result.loaded[name] = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            result.errors.append(f"{name}: cannot read UTF-8 content: {exc}")


def _read_optional_files(root: Path, result: BundleResult) -> None:
    for name in OPTIONAL_FILES:
        candidate = root / name
        if not candidate.exists():
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            result.warnings.append(f"{name}: cannot resolve: {exc}")
            continue
        if not _is_within(resolved, root) or not resolved.is_file():
            result.warnings.append(f"{name}: ignored (not a file inside state root)")
            continue
        try:
            result.loaded[name] = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            result.warnings.append(f"{name}: cannot read UTF-8 content: {exc}")
            continue
        if name == "hunt-plan.md":
            _validate_hunt_plan_overlay(result.loaded[name], result.warnings)


def _parse_markdown_meta(
    name: str,
    content: str,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any] | None:
    lines = content.splitlines()
    expected = MARKDOWN_HEADINGS[name]
    if not lines or lines[0].strip() != expected:
        errors.append(f"{name}: first line must be {expected!r}")
    if len(lines) < 2:
        warnings.append(f"{name}: missing v2 metadata comment")
        return None
    match = MARKDOWN_META_RE.fullmatch(lines[1].strip())
    if not match:
        warnings.append(f"{name}: second line is not v2 metadata")
        return None
    try:
        value = json.loads(match.group("meta"))
    except json.JSONDecodeError as exc:
        errors.append(f"{name}: invalid metadata JSON: {exc.msg}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{name}: metadata must be an object")
        return None
    return value


def _parse_json_file(
    name: str,
    content: str,
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        errors.append(f"{name}: invalid JSON at line {exc.lineno}: {exc.msg}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{name}: top level must be an object")
        return None
    return value


def _validate_session(
    session: dict[str, Any],
    state_ids: set[str],
    errors: list[str],
) -> None:
    if session.get("mode") not in {"pentest", "ctf"}:
        errors.append("session-index.json: mode must be pentest or ctf")
    scope = session.get("scope")
    if not isinstance(scope, list) or not all(isinstance(x, str) for x in scope):
        errors.append("session-index.json: scope must be an array of strings")
    targets = session.get("targets")
    if not isinstance(targets, list):
        errors.append("session-index.json: targets must be an array")
        return
    for index, target in enumerate(targets):
        if not isinstance(target, dict):
            errors.append(f"session-index.json: targets[{index}] must be an object")
            continue
        target_id = target.get("id")
        if (
            not isinstance(target_id, str)
            or not target_id.startswith("A-")
            or target_id not in state_ids
        ):
            errors.append(
                f"session-index.json: targets[{index}].id {target_id!r} "
                "does not exist in core state"
            )
        if not isinstance(target.get("ip"), str):
            errors.append(f"session-index.json: targets[{index}].ip must be a string")
        if not isinstance(target.get("hostname"), str):
            errors.append(
                f"session-index.json: targets[{index}].hostname must be a string"
            )
        if target.get("status") not in {"active", "completed", "parked"}:
            errors.append(
                f"session-index.json: targets[{index}].status has an invalid value"
            )
    last_stop = session.get("last_stop")
    if last_stop is not None:
        if not isinstance(last_stop, dict):
            errors.append("session-index.json: last_stop must be an object")
        else:
            for field_name, prefix in (("route", "R-"), ("hypothesis", "H-")):
                ref = last_stop.get(field_name)
                if ref is not None and (
                    not isinstance(ref, str)
                    or not ref.startswith(prefix)
                    or ref not in state_ids
                ):
                    errors.append(
                        f"session-index.json: last_stop.{field_name} "
                        f"{ref!r} does not exist in core state"
                    )


def _declared_state_ids(
    name: str,
    content: str,
    errors: list[str],
) -> set[str]:
    expected_prefixes = {
        "asset-graph.md": {"A-"},
        "route-stack.md": {"R-", "H-"},
        "loot-tracker.md": {"L-"},
    }[name]
    declared = TABLE_ID_RE.findall(content)
    if name == "route-stack.md":
        declared.extend(ACTIVE_HYPOTHESIS_ID_RE.findall(content))
    filtered = [
        state_id
        for state_id in declared
        if any(state_id.startswith(prefix) for prefix in expected_prefixes)
    ]
    for state_id, count in Counter(filtered).items():
        if count > 1:
            errors.append(f"{name}: stable ID {state_id!r} is declared {count} times")
    return set(filtered)


def _safe_artifact_path(
    raw_path: Any,
    root: Path,
) -> tuple[Path | None, str | None]:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, "path must be a non-empty string"
    if "\\" in raw_path:
        return None, "path must use POSIX separators"
    pure = PurePosixPath(raw_path)
    if pure.is_absolute() or ".." in pure.parts:
        return None, "path must be relative and may not contain '..'"
    resolved = (root / Path(*pure.parts)).resolve(strict=False)
    if not _is_within(resolved, root):
        return None, "resolved path escapes state root"
    return resolved, None


def _validate_evidence(
    evidence: dict[str, Any],
    state_ids: set[str],
    root: Path,
    errors: list[str],
    warnings: list[str],
) -> None:
    entries = evidence.get("entries")
    if not isinstance(entries, list):
        errors.append("evidence-index.json: entries must be an array")
        return

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        prefix = f"evidence-index.json: entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue

        evidence_id = entry.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID_RE.fullmatch(
            evidence_id
        ):
            errors.append(f"{prefix}.id must match E-*")
        elif evidence_id in seen:
            errors.append(f"{prefix}.id {evidence_id!r} is duplicated")
        else:
            seen.add(evidence_id)

        refs = entry.get("state_refs")
        if (
            not isinstance(refs, list)
            or not refs
            or not all(isinstance(ref, str) for ref in refs)
        ):
            errors.append(f"{prefix}.state_refs must be a non-empty string array")
        else:
            for ref in refs:
                if ref not in state_ids:
                    errors.append(f"{prefix}.state_refs contains unknown ID {ref!r}")

        if not isinstance(entry.get("claim"), str) or not entry["claim"].strip():
            errors.append(f"{prefix}.claim must be a non-empty string")
        if entry.get("relation") not in RELATIONS:
            errors.append(f"{prefix}.relation must be supports or refutes")
        if entry.get("confidence") not in CONFIDENCE:
            errors.append(f"{prefix}.confidence must be high, medium, or low")
        if entry.get("freshness") not in FRESHNESS:
            errors.append(f"{prefix}.freshness has an invalid value")

        verified = entry.get("last_verified")
        if verified is not None and not _iso_with_timezone(verified):
            errors.append(
                f"{prefix}.last_verified must be null or ISO 8601 with timezone"
            )

        availability = entry.get("availability")
        if availability not in AVAILABILITY:
            errors.append(f"{prefix}.availability has an invalid value")

        artifacts = entry.get("artifacts")
        if not isinstance(artifacts, list):
            errors.append(f"{prefix}.artifacts must be an array")
            continue
        if availability == "saved" and not artifacts:
            warnings.append(f"{prefix}: saved evidence has no artifact locator")

        for artifact_index, artifact in enumerate(artifacts):
            artifact_prefix = f"{prefix}.artifacts[{artifact_index}]"
            if not isinstance(artifact, dict):
                errors.append(f"{artifact_prefix} must be an object")
                continue
            resolved, path_error = _safe_artifact_path(artifact.get("path"), root)
            if path_error:
                errors.append(f"{artifact_prefix}: {path_error}")
                continue
            if not isinstance(artifact.get("kind"), str) or not artifact[
                "kind"
            ].strip():
                errors.append(f"{artifact_prefix}.kind must be a non-empty string")
            locator = artifact.get("locator")
            if locator is not None and not isinstance(locator, str):
                errors.append(f"{artifact_prefix}.locator must be a string")
            digest = artifact.get("sha256")
            if digest is not None and (
                not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
            ):
                errors.append(
                    f"{artifact_prefix}.sha256 must be 64 lowercase hex characters"
                )
            if availability == "saved" and resolved is not None:
                if not resolved.exists():
                    warnings.append(
                        f"{artifact_prefix}: saved artifact is missing: "
                        f"{artifact.get('path')}"
                    )
                elif not resolved.is_file():
                    warnings.append(
                        f"{artifact_prefix}: artifact path is not a regular file"
                    )


def _import_hunt_plan():
    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))
    import hunt_plan

    return hunt_plan


def _brief_hunt_plan_lines(text: str) -> list[str]:
    """Stance, gaps, and live bets. The plan file itself stays on disk."""
    byte_len = len(text.encode("utf-8"))
    lines = [f"OVERLAY hunt-plan.md: {byte_len} bytes (not dumped)"]
    try:
        hunt_plan = _import_hunt_plan()
    except ImportError as exc:
        lines.append(f"OVERLAY hunt-plan.md: unparsed ({exc})")
        return lines
    try:
        plan = hunt_plan.parse_hunt_plan(text)
    except hunt_plan.HuntPlanError as exc:
        lines.append(f"OVERLAY hunt-plan.md: unparsed ({exc})")
        return lines
    lines.append(hunt_plan.render_stance_line(plan))
    gaps = hunt_plan.observation_gaps(plan)
    if gaps:
        lines.extend(f"gap:{item}" for item in gaps)
    else:
        lines.append("gaps=none")
    for bet in hunt_plan.active_bets(plan):
        lines.append(
            f"bet {bet.id} rank={bet.rank} status={bet.status} "
            f"claim={bet.claim} probe={bet.probe} "
            f"expect={bet.expect} kill_if={bet.kill_if}"
        )
    killed = [bet.id for bet in plan.bets if bet.status == "killed"]
    if killed:
        lines.append("killed=" + ",".join(killed))
    return lines


def _validate_hunt_plan_overlay(text: str, warnings: list[str]) -> None:
    try:
        hunt_plan = _import_hunt_plan()
    except ImportError as exc:
        warnings.append(f"hunt-plan.md: cannot import hunt_plan: {exc}")
        return
    try:
        errors = hunt_plan.validate_hunt_plan(hunt_plan.parse_hunt_plan(text))
    except hunt_plan.HuntPlanError as exc:
        warnings.append(f"hunt-plan.md: {exc}")
        return
    warnings.extend(f"hunt-plan.md: {item}" for item in errors)


def load_bundle(path: Path) -> BundleResult:
    requested = path.expanduser()
    try:
        root = requested.resolve(strict=True)
    except OSError:
        return BundleResult(
            root=requested.absolute(),
            status=2,
            errors=["state root does not exist or cannot be resolved"],
        )
    if not root.is_dir():
        return BundleResult(
            root=root,
            status=2,
            errors=["state root is not a directory"],
        )

    result = BundleResult(root=root, status=1)
    _read_core_files(root, result)
    _read_optional_files(root, result)
    core_loaded = {
        name: content
        for name, content in result.loaded.items()
        if name in CORE_FILES
    }
    if not any(content.strip() for content in core_loaded.values()):
        result.status = 2
        result.errors.append("no usable core state content")
        return result

    metadata: dict[str, dict[str, Any] | None] = {}
    json_docs: dict[str, dict[str, Any] | None] = {}

    for name in MARKDOWN_HEADINGS:
        if name in result.loaded:
            metadata[name] = _parse_markdown_meta(
                name, result.loaded[name], result.errors, result.warnings
            )
    for name in ("session-index.json", "evidence-index.json"):
        if name in result.loaded:
            parsed = _parse_json_file(name, result.loaded[name], result.errors)
            json_docs[name] = parsed
            metadata[name] = parsed

    schemas: list[int] = []
    checkpoints: list[str] = []
    timestamps: list[str] = []
    for name in CORE_FILES:
        if name not in result.loaded:
            continue
        schema, checkpoint, updated = _validate_bundle_meta(
            name, metadata.get(name), result.errors, result.warnings
        )
        if schema is not None:
            schemas.append(schema)
        if checkpoint is not None:
            checkpoints.append(checkpoint)
        if updated is not None:
            timestamps.append(updated)

    if len(set(checkpoints)) > 1:
        result.errors.append(
            "checkpoint_id mismatch across core files: "
            + ", ".join(sorted(set(checkpoints)))
        )
    if len(set(timestamps)) > 1:
        result.errors.append("last_updated mismatch across core files")

    state_ids: set[str] = set()
    for name in MARKDOWN_HEADINGS:
        content = result.loaded.get(name)
        if content:
            state_ids.update(_declared_state_ids(name, content, result.errors))

    session = json_docs.get("session-index.json")
    if session is not None:
        _validate_session(session, state_ids, result.errors)
    evidence = json_docs.get("evidence-index.json")
    if evidence is not None:
        _validate_evidence(
            evidence, state_ids, root, result.errors, result.warnings
        )

    core_names = {name for name in result.loaded if name in CORE_FILES}
    complete = (
        core_names == set(CORE_FILES)
        and len(schemas) == len(CORE_FILES)
        and all(schema == 2 for schema in schemas)
        and len(checkpoints) == len(CORE_FILES)
        and len(set(checkpoints)) == 1
        and len(timestamps) == len(CORE_FILES)
        and len(set(timestamps)) == 1
        and not result.errors
        and not result.warnings
    )
    result.status = 0 if complete else 1
    return result


def _meta(checkpoint: str) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "checkpoint_id": checkpoint,
        "last_updated": "2026-07-21T14:25:00+08:00",
    }


def _metadata_comment(checkpoint: str) -> str:
    payload = json.dumps(_meta(checkpoint), separators=(",", ":"))
    return f"<!-- huntboard-state: {payload} -->"


def _write_complete_fixture(root: Path, checkpoint: str = "cp-1") -> None:
    root.mkdir(parents=True, exist_ok=True)
    comment = _metadata_comment(checkpoint)
    session = {
        **_meta(checkpoint),
        "targets": [
            {
                "id": "A-0001",
                "ip": "10.10.10.5",
                "hostname": "web01.local",
                "status": "active",
            }
        ],
        "scope": ["10.10.10.5"],
        "mode": "ctf",
        "last_stop": {
            "route": "R-0001",
            "hypothesis": "H-0001",
            "summary": "test",
        },
    }
    (root / "session-index.json").write_text(
        json.dumps(session), encoding="utf-8"
    )
    (root / "asset-graph.md").write_text(
        "\n".join(
            [
                "# Asset Graph",
                comment,
                "",
                "| ID | Host |",
                "|----|------|",
                "| A-0001 | 10.10.10.5 |",
            ]
        ),
        encoding="utf-8",
    )
    (root / "route-stack.md").write_text(
        "\n".join(
            [
                "# Route Stack",
                comment,
                "",
                "| ID | Route |",
                "|----|-------|",
                "| R-0001 | Web & API |",
                "",
                "1. **[H-0001] [HIGH]** test",
            ]
        ),
        encoding="utf-8",
    )
    (root / "loot-tracker.md").write_text(
        "\n".join(
            [
                "# Loot Tracker",
                comment,
                "",
                "| ID | Type |",
                "|----|------|",
                "| L-0001 | token |",
            ]
        ),
        encoding="utf-8",
    )
    artifact = root / "loot" / "evidence.txt"
    artifact.parent.mkdir()
    artifact.write_text("DO-NOT-PRELOAD-SENTINEL", encoding="utf-8")
    evidence = {
        **_meta(checkpoint),
        "entries": [
            {
                "id": "E-0001",
                "state_refs": ["A-0001", "R-0001", "H-0001", "L-0001"],
                "claim": "fixture claim",
                "relation": "supports",
                "confidence": "high",
                "freshness": "stable",
                "last_verified": "2026-07-21T14:25:00+08:00",
                "availability": "saved",
                "artifacts": [
                    {
                        "path": "loot/evidence.txt",
                        "kind": "fixture",
                        "locator": "line=1",
                    }
                ],
            }
        ],
    }
    (root / "evidence-index.json").write_text(
        json.dumps(evidence), encoding="utf-8"
    )


def _run_self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="huntboard-state-test-") as temp:
        base = Path(temp)

        complete_root = base / "complete"
        _write_complete_fixture(complete_root)
        complete = load_bundle(complete_root)
        if complete.status != 0:
            failures.append(
                f"complete fixture expected 0, got {complete.status}: "
                f"{complete.errors} {complete.warnings}"
            )
        if "DO-NOT-PRELOAD-SENTINEL" in complete.render():
            failures.append("artifact body leaked into complete loader output")
        brief = complete.render()
        if "BEGIN CORE FILE:" in brief:
            failures.append("default render dumped core file bodies")
        if "| L-0001 |" in brief:
            failures.append("loot-tracker body leaked into brief render")
        full = complete.render(full=True)
        if "BEGIN CORE FILE: loot-tracker.md" not in full:
            failures.append("--full must dump core file bodies")
        if "DO-NOT-PRELOAD-SENTINEL" in full:
            failures.append("artifact body leaked into --full loader output")

        overlay_root = base / "overlay"
        _write_complete_fixture(overlay_root)
        if str(_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(_SCRIPTS_DIR))
        import hunt_plan

        plan = hunt_plan.parse_hunt_plan(
            "\n".join(
                [
                    "# Hunt Plan",
                    "phase: EXECUTE",
                    "goal: 取得具名身份",
                    "have: anonymous",
                    "next_probe: LDAP rootDSE",
                    "attempts: 0",
                    "untested: 無",
                    "adjust: stay",
                    "wildcard:",
                    "materials: read",
                    "surface.transport: seen",
                    "surface.identity_unauth: seen",
                    "surface.naming: seen",
                    "surface.materials: seen",
                    "bet.H-1.rank: 1",
                    "bet.H-1.claim: 未認證目錄",
                    "bet.H-1.probe: LDAP rootDSE",
                    "bet.H-1.expect: naming context",
                    "bet.H-1.kill_if: 不可達",
                    "bet.H-1.status: active",
                    "last_observed: DO-NOT-BRIEF-OBSERVED",
                ]
            )
        )
        (overlay_root / "hunt-plan.md").write_text(
            hunt_plan.render_hunt_plan(plan), encoding="utf-8"
        )
        overlay = load_bundle(overlay_root)
        if overlay.status != 0:
            failures.append(
                f"valid hunt-plan overlay expected 0, got {overlay.status}: "
                f"{overlay.errors} {overlay.warnings}"
            )
        rendered = overlay.render()
        if "BEGIN OVERLAY FILE: hunt-plan.md" in rendered:
            failures.append("brief render dumped hunt-plan body")
        if "DO-NOT-BRIEF-OBSERVED" in rendered:
            failures.append("brief render dumped last_observed")
        if "OVERLAY hunt-plan.md:" not in rendered or "not dumped" not in rendered:
            failures.append("brief render missing hunt-plan size line")
        if "態勢：Phase=EXECUTE" not in rendered or "Goal=取得具名身份" not in rendered:
            failures.append("brief render missing stance line")
        if "gaps=none" not in rendered:
            failures.append("complete hunt-plan brief must report gaps=none")
        if "bet H-1 " not in rendered or "expect=naming context" not in rendered:
            failures.append("brief render missing active bet")
        full_overlay = overlay.render(full=True)
        if "BEGIN OVERLAY FILE: hunt-plan.md" not in full_overlay:
            failures.append("--full must dump hunt-plan overlay")
        if "goal: 取得具名身份" not in full_overlay:
            failures.append("hunt-plan overlay body missing from --full output")
        if "DO-NOT-BRIEF-OBSERVED" not in full_overlay:
            failures.append("--full must keep last_observed")

        broken_overlay = base / "broken-overlay"
        _write_complete_fixture(broken_overlay)
        (broken_overlay / "hunt-plan.md").write_text(
            "phase: NOPE\n", encoding="utf-8"
        )
        broken = load_bundle(broken_overlay)
        if broken.status != 1 or not any(
            "hunt-plan.md" in item for item in broken.warnings
        ):
            failures.append("invalid hunt-plan overlay must warn and degrade")

        legacy_root = base / "legacy"
        legacy_root.mkdir()
        (legacy_root / "session-index.json").write_text(
            json.dumps(
                {
                    "targets": [],
                    "scope": ["legacy.local"],
                    "mode": "ctf",
                    "last_updated": "2026-07-21T14:25:00+08:00",
                }
            ),
            encoding="utf-8",
        )
        for name, heading in MARKDOWN_HEADINGS.items():
            (legacy_root / name).write_text(f"{heading}\n\nlegacy\n", encoding="utf-8")
        if load_bundle(legacy_root).status != 1:
            failures.append("legacy four-file fixture must degrade with exit 1")

        partial_root = base / "partial"
        partial_root.mkdir()
        (partial_root / "asset-graph.md").write_text(
            "# Asset Graph\nbroken metadata\n", encoding="utf-8"
        )
        (partial_root / "session-index.json").write_text("{broken", encoding="utf-8")
        partial = load_bundle(partial_root)
        if partial.status != 1 or len(
            [name for name in partial.loaded if name in CORE_FILES]
        ) != 2:
            failures.append("partial invalid fixture must retain readable files")

        mismatch_root = base / "mismatch"
        _write_complete_fixture(mismatch_root)
        evidence = json.loads(
            (mismatch_root / "evidence-index.json").read_text(encoding="utf-8")
        )
        evidence["checkpoint_id"] = "cp-other"
        (mismatch_root / "evidence-index.json").write_text(
            json.dumps(evidence), encoding="utf-8"
        )
        mismatch = load_bundle(mismatch_root)
        if mismatch.status != 1 or not any(
            "mismatch" in error for error in mismatch.errors
        ):
            failures.append("checkpoint mismatch fixture was not rejected")

        traversal_root = base / "traversal"
        _write_complete_fixture(traversal_root)
        evidence = json.loads(
            (traversal_root / "evidence-index.json").read_text(encoding="utf-8")
        )
        evidence["entries"][0]["artifacts"][0]["path"] = "../escape.txt"
        (traversal_root / "evidence-index.json").write_text(
            json.dumps(evidence), encoding="utf-8"
        )
        traversal = load_bundle(traversal_root)
        if traversal.status != 1 or not any(
            "may not contain" in error for error in traversal.errors
        ):
            failures.append("artifact path traversal fixture was not rejected")

        unknown_ref_root = base / "unknown-ref"
        _write_complete_fixture(unknown_ref_root)
        evidence = json.loads(
            (unknown_ref_root / "evidence-index.json").read_text(encoding="utf-8")
        )
        evidence["entries"][0]["state_refs"] = ["A-9999"]
        (unknown_ref_root / "evidence-index.json").write_text(
            json.dumps(evidence), encoding="utf-8"
        )
        unknown_ref = load_bundle(unknown_ref_root)
        if unknown_ref.status != 1 or not any(
            "unknown ID" in error for error in unknown_ref.errors
        ):
            failures.append("unknown state reference fixture was not rejected")

        duplicate_id_root = base / "duplicate-id"
        _write_complete_fixture(duplicate_id_root)
        route_path = duplicate_id_root / "route-stack.md"
        route_path.write_text(
            route_path.read_text(encoding="utf-8")
            + "\n2. **[H-0001] [LOW]** duplicate\n",
            encoding="utf-8",
        )
        duplicate_id = load_bundle(duplicate_id_root)
        if duplicate_id.status != 1 or not any(
            "declared 2 times" in error for error in duplicate_id.errors
        ):
            failures.append("duplicate stable ID fixture was not rejected")

        empty_root = base / "empty"
        empty_root.mkdir()
        if load_bundle(empty_root).status != 2:
            failures.append("empty fixture must return exit 2")

        stamp_empty = base / "stamp-empty"
        stamped = stamp_bundle(stamp_empty, checkpoint_id="cp-stamp")
        if stamped.status != 0:
            failures.append(
                f"stamp empty dir expected 0, got {stamped.status}: "
                f"{stamped.errors} {stamped.warnings}"
            )
        if stamped.loaded.get("session-index.json") and (
            "cp-stamp" not in stamped.loaded["session-index.json"]
        ):
            failures.append("stamp did not write checkpoint_id")

        mismatch_stamped = base / "mismatch-stamped"
        _write_complete_fixture(mismatch_stamped)
        evidence = json.loads(
            (mismatch_stamped / "evidence-index.json").read_text(encoding="utf-8")
        )
        evidence["checkpoint_id"] = "cp-other"
        (mismatch_stamped / "evidence-index.json").write_text(
            json.dumps(evidence), encoding="utf-8"
        )
        aligned = stamp_bundle(mismatch_stamped, checkpoint_id="cp-aligned")
        if aligned.status != 0:
            failures.append(
                f"stamp mismatch expected 0, got {aligned.status}: "
                f"{aligned.errors} {aligned.warnings}"
            )
        if "DO-NOT-PRELOAD-SENTINEL" in aligned.render():
            failures.append("stamp leaked artifact body")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print(
        "PASS: complete, overlay, broken-overlay, legacy, partial, mismatch, "
        "traversal, references, stable IDs, lazy-artifact, and stamp"
    )
    return 0


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _new_checkpoint_id() -> str:
    return datetime.now().astimezone().strftime("cp-%Y%m%d-%H%M%S")


def _stamp_markdown(path: Path, heading: str, comment: str) -> None:
    if not path.exists():
        path.write_text(f"{heading}\n{comment}\n\n", encoding="utf-8")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        path.write_text(f"{heading}\n{comment}\n", encoding="utf-8")
        return
    if lines[0].strip() != heading:
        lines = [heading, comment, *lines]
    elif len(lines) > 1 and MARKDOWN_META_RE.fullmatch(lines[1].strip()):
        lines[1] = comment
    else:
        lines.insert(1, comment)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stamp_json(
    path: Path,
    meta: dict[str, Any],
    *,
    scaffold: dict[str, Any],
    last_stop: Any | None,
) -> None:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = dict(scaffold)
        except json.JSONDecodeError:
            data = dict(scaffold)
    else:
        data = dict(scaffold)
    data["schema_version"] = 2
    data["checkpoint_id"] = meta["checkpoint_id"]
    data["last_updated"] = meta["last_updated"]
    if last_stop is not None:
        data["last_stop"] = last_stop
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def stamp_bundle(
    root: Path,
    *,
    checkpoint_id: str | None = None,
    last_stop: Any | None = None,
) -> BundleResult:
    root.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": 2,
        "checkpoint_id": checkpoint_id or _new_checkpoint_id(),
        "last_updated": _now_iso(),
    }
    comment = (
        "<!-- huntboard-state: "
        + json.dumps(meta, separators=(",", ":"))
        + " -->"
    )
    for name, heading in MARKDOWN_HEADINGS.items():
        _stamp_markdown(root / name, heading, comment)
    _stamp_json(
        root / "session-index.json",
        meta,
        scaffold={
            "mode": "ctf",
            "scope": [],
            "targets": [],
            "last_stop": {"reason": "checkpoint"},
        },
        last_stop=last_stop,
    )
    _stamp_json(
        root / "evidence-index.json",
        meta,
        scaffold={"entries": []},
        last_stop=None,
    )
    return load_bundle(root)


def _parse_last_stop(raw: str | None) -> Any | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    if text.startswith("{") or text.startswith("["):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return {"reason": "checkpoint", "summary": text}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate core state files without reading indexed evidence "
            "artifacts. Default stdout is a brief summary; --full dumps "
            "core file bodies. --stamp writes aligned metadata."
        )
    )
    parser.add_argument(
        "state_dir",
        nargs="?",
        default="./pentest-state",
        type=Path,
        help="state bundle directory (default: ./pentest-state)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run isolated loader fixtures and exit",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "dump core file bodies and hunt-plan overlay "
            "(default: brief summary; hunt-plan is stance, gaps, active bets)"
        ),
    )
    parser.add_argument(
        "--stamp",
        action="store_true",
        help="align checkpoint metadata on core files; scaffold if missing",
    )
    parser.add_argument(
        "--id",
        dest="checkpoint_id",
        default=None,
        help="checkpoint_id for --stamp (default: cp-YYYYMMDD-HHMMSS)",
    )
    parser.add_argument(
        "--last-stop",
        dest="last_stop",
        default=None,
        help="session last_stop JSON object or one-line summary (stamp only)",
    )
    args = parser.parse_args(argv)
    if args.self_test:
        return _run_self_test()
    if args.stamp:
        result = stamp_bundle(
            args.state_dir,
            checkpoint_id=args.checkpoint_id,
            last_stop=_parse_last_stop(args.last_stop),
        )
        sys.stdout.write(result.render(full=args.full))
        return result.status
    result = load_bundle(args.state_dir)
    sys.stdout.write(result.render(full=args.full))
    return result.status


if __name__ == "__main__":
    raise SystemExit(main())
