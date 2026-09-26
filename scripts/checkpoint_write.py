#!/usr/bin/env python3
"""Write a valid pentest-state bundle from one facts JSON.

Combat path: assemble facts once, run this script once. The script renders the
five core files and optional hunt-plan overlay, aligns metadata, and validates
with load_state_bundle. On failure the original state directory is left
untouched. Do not hand-write core files. Do not read this source in combat;
run ``--print-schema`` if the field list is needed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import hunt_plan  # noqa: E402
import load_state_bundle  # noqa: E402


STABLE_ID = re.compile(r"^[ARHL]-\d+$")
EVIDENCE_ID = re.compile(r"^E-\d+$")
HYP_ID = re.compile(r"^H-\d+$")
PRIORITIES = {"HIGH", "MED", "LOW"}
TARGET_STATUSES = {"active", "completed", "parked"}
MODES = {"pentest", "ctf"}
RELATIONS = {"supports", "refutes"}
CONFIDENCE = {"high", "medium", "low"}
FRESHNESS = {"stable", "time-bound", "session-bound", "unknown"}
AVAILABILITY = {"saved", "not-saved", "missing"}
HYP_STATUSES = {"active", "closed", "paused"}

SCHEMA_EXAMPLE = """\
{
  "mode": "ctf",
  "scope": ["10.0.0.1", "dc.example.vl"],
  "targets": [
    {"id": "A-0001", "ip": "10.0.0.1", "hostname": "dc.example.vl", "status": "active"}
  ],
  "assets": [
    {"id": "A-0001", "label": "DC", "kind": "host", "address": "10.0.0.1 / dc.example.vl", "state": "可達", "notes": "banner"}
  ],
  "routes": [
    {"id": "R-0001", "name": "Identity & Trust", "status": "active", "focus": "下一觀看者剩餘觀察"}
  ],
  "hypotheses": [
    {"id": "H-0001", "priority": "HIGH", "claim": "新身分能讀 guest 讀不到的材料", "probe": "smb/ldap as that user", "kill_if": "全 ACCESS_DENIED", "status": "active"}
  ],
  "closed": [
    {"id": "H-0002", "claim": "入職密碼對信裡兩帳有效", "status": "closed", "reopen_if": "發現別名"}
  ],
  "loot": [
    {"id": "L-0001", "kind": "password", "value": "example", "source": "Public pdf", "state": "已用", "use": "對 ibryant 有效"}
  ],
  "evidence": [
    {
      "id": "E-0001",
      "state_refs": ["A-0001", "R-0001", "H-0001"],
      "claim": "10.0.0.1 是網域控制站",
      "relation": "supports",
      "confidence": "high",
      "freshness": "stable",
      "last_verified": "2026-09-21T12:00:00+08:00",
      "availability": "saved",
      "artifacts": [{"path": "loot/nxc-smb-unauth.txt", "kind": "nxc", "locator": "banner"}]
    }
  ],
  "last_stop": {
    "route": "R-0001",
    "hypothesis": "H-0001",
    "summary": "停在新身分剩餘觀察，尚未執行。"
  },
  "hunt_plan": {
    "phase": "OBSERVE",
    "goal": "用新身分看清網域",
    "have": "identity=example",
    "next_probe": "smb --shares 與 ldap --users",
    "attempts": 0,
    "untested": "該觀看者 shares/LDAP",
    "adjust": "re-observe",
    "wildcard": "",
    "materials": "read",
    "last_expected": "真登入",
    "last_observed": "已證實 SMB [+]",
    "surfaces": {
      "transport": "seen",
      "identity_unauth": "seen",
      "naming": "seen",
      "materials": "seen"
    },
    "bets": [
      {"id": "H-view", "rank": 1, "claim": "能讀目錄", "probe": "ldap as user", "expect": "物件列表", "kill_if": "ACCESS_DENIED", "status": "active"}
    ]
  }
}
"""


class CheckpointError(ValueError):
    """Facts JSON cannot be rendered into a valid bundle."""


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _new_checkpoint_id() -> str:
    return datetime.now().astimezone().strftime("cp-%Y%m%d-%H%M%S")


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.split())
    return text.replace("|", "/")


def _require_id(value: Any, prefix: str, where: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}: id is required")
        return None
    ident = value.strip()
    if prefix == "E-":
        if not EVIDENCE_ID.fullmatch(ident):
            errors.append(f"{where}: id {ident!r} must match E-<digits>")
            return None
        return ident
    if prefix == "H-" and not HYP_ID.fullmatch(ident):
        errors.append(
            f"{where}: id {ident!r} must match H-<digits> (route-stack hypotheses)"
        )
        return None
    if prefix != "H-" and not (STABLE_ID.fullmatch(ident) and ident.startswith(prefix)):
        errors.append(f"{where}: id {ident!r} must match {prefix}<digits>")
        return None
    return ident


def _as_list(value: Any, where: str, errors: list[str]) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        errors.append(f"{where} must be an array")
        return []
    return value


def _as_object(value: Any, where: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{where} must be an object")
        return None
    return value


def validate_facts(facts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if facts.get("mode") not in MODES:
        errors.append("mode must be pentest or ctf")
    scope = facts.get("scope")
    if not isinstance(scope, list) or not scope or not all(
        isinstance(item, str) and item.strip() for item in scope
    ):
        errors.append("scope must be a non-empty array of strings")

    assets = _as_list(facts.get("assets"), "assets", errors)
    routes = _as_list(facts.get("routes"), "routes", errors)
    hypotheses = _as_list(facts.get("hypotheses"), "hypotheses", errors)
    closed = _as_list(facts.get("closed"), "closed", errors)
    loot = _as_list(facts.get("loot"), "loot", errors)
    evidence = _as_list(facts.get("evidence"), "evidence", errors)
    targets = _as_list(facts.get("targets"), "targets", errors)

    asset_ids: set[str] = set()
    route_ids: set[str] = set()
    hyp_ids: set[str] = set()
    loot_ids: set[str] = set()

    if not assets:
        errors.append("assets must contain at least one host/domain object")
    for index, item in enumerate(assets):
        obj = _as_object(item, f"assets[{index}]", errors)
        if obj is None:
            continue
        ident = _require_id(obj.get("id"), "A-", f"assets[{index}]", errors)
        if ident:
            if ident in asset_ids:
                errors.append(f"assets: duplicate id {ident}")
            asset_ids.add(ident)
        if not str(obj.get("label") or obj.get("host") or "").strip():
            errors.append(f"assets[{index}]: label is required")

    if not routes:
        errors.append("routes must contain at least one route")
    for index, item in enumerate(routes):
        obj = _as_object(item, f"routes[{index}]", errors)
        if obj is None:
            continue
        ident = _require_id(obj.get("id"), "R-", f"routes[{index}]", errors)
        if ident:
            if ident in route_ids:
                errors.append(f"routes: duplicate id {ident}")
            route_ids.add(ident)
        if not str(obj.get("name") or "").strip():
            errors.append(f"routes[{index}]: name is required")

    for index, item in enumerate(hypotheses):
        obj = _as_object(item, f"hypotheses[{index}]", errors)
        if obj is None:
            continue
        ident = _require_id(obj.get("id"), "H-", f"hypotheses[{index}]", errors)
        status = obj.get("status", "active")
        if status not in HYP_STATUSES:
            errors.append(f"hypotheses[{index}]: status must be active, closed, or paused")
        if ident:
            if ident in hyp_ids:
                errors.append(f"hypotheses: duplicate id {ident}")
            hyp_ids.add(ident)
        if not str(obj.get("claim") or "").strip():
            errors.append(f"hypotheses[{index}]: claim is required")
        priority = obj.get("priority", "HIGH")
        if priority not in PRIORITIES:
            errors.append(f"hypotheses[{index}]: priority must be HIGH, MED, or LOW")

    for index, item in enumerate(closed):
        obj = _as_object(item, f"closed[{index}]", errors)
        if obj is None:
            continue
        ident = _require_id(obj.get("id"), "H-", f"closed[{index}]", errors)
        if ident:
            if ident in hyp_ids:
                errors.append(f"closed: duplicate id {ident}")
            hyp_ids.add(ident)
        if not str(obj.get("claim") or "").strip():
            errors.append(f"closed[{index}]: claim is required")

    for index, item in enumerate(loot):
        obj = _as_object(item, f"loot[{index}]", errors)
        if obj is None:
            continue
        ident = _require_id(obj.get("id"), "L-", f"loot[{index}]", errors)
        if ident:
            if ident in loot_ids:
                errors.append(f"loot: duplicate id {ident}")
            loot_ids.add(ident)
        if not str(obj.get("kind") or "").strip():
            errors.append(f"loot[{index}]: kind is required")

    if not targets:
        errors.append("targets must contain at least one session target")
    for index, item in enumerate(targets):
        obj = _as_object(item, f"targets[{index}]", errors)
        if obj is None:
            continue
        ident = obj.get("id")
        if ident not in asset_ids:
            errors.append(f"targets[{index}].id {ident!r} is not in assets")
        if not isinstance(obj.get("ip"), str):
            errors.append(f"targets[{index}].ip must be a string")
        if not isinstance(obj.get("hostname"), str):
            errors.append(f"targets[{index}].hostname must be a string")
        if obj.get("status") not in TARGET_STATUSES:
            errors.append(f"targets[{index}].status must be active, completed, or parked")

    state_ids = asset_ids | route_ids | hyp_ids | loot_ids
    last_stop = facts.get("last_stop")
    if last_stop is None:
        errors.append("last_stop is required")
    else:
        obj = _as_object(last_stop, "last_stop", errors)
        if obj is not None:
            if not str(obj.get("summary") or "").strip():
                errors.append("last_stop.summary is required")
            route = obj.get("route")
            if route is not None and route not in route_ids:
                errors.append(f"last_stop.route {route!r} is not in routes")
            hypothesis = obj.get("hypothesis")
            if hypothesis is not None and hypothesis not in hyp_ids:
                errors.append(
                    f"last_stop.hypothesis {hypothesis!r} is not in hypotheses/closed"
                )

    seen_evidence: set[str] = set()
    for index, item in enumerate(evidence):
        obj = _as_object(item, f"evidence[{index}]", errors)
        if obj is None:
            continue
        ident = _require_id(obj.get("id"), "E-", f"evidence[{index}]", errors)
        if ident:
            if ident in seen_evidence:
                errors.append(f"evidence: duplicate id {ident}")
            seen_evidence.add(ident)
        refs = obj.get("state_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"evidence[{index}].state_refs must be a non-empty array")
        else:
            for ref in refs:
                if ref not in state_ids:
                    errors.append(
                        f"evidence[{index}].state_refs contains unknown ID {ref!r}"
                    )
        if not str(obj.get("claim") or "").strip():
            errors.append(f"evidence[{index}].claim is required")
        if obj.get("relation") not in RELATIONS:
            errors.append(f"evidence[{index}].relation must be supports or refutes")
        if obj.get("confidence") not in CONFIDENCE:
            errors.append(f"evidence[{index}].confidence must be high, medium, or low")
        if obj.get("freshness") not in FRESHNESS:
            errors.append(f"evidence[{index}].freshness has an invalid value")
        if obj.get("availability") not in AVAILABILITY:
            errors.append(f"evidence[{index}].availability has an invalid value")
        verified = obj.get("last_verified")
        if verified is not None:
            try:
                parsed = datetime.fromisoformat(str(verified).replace("Z", "+00:00"))
            except ValueError:
                parsed = None
            if parsed is None or parsed.tzinfo is None:
                errors.append(
                    f"evidence[{index}].last_verified must be ISO 8601 with timezone"
                )
        artifacts = obj.get("artifacts", [])
        if not isinstance(artifacts, list):
            errors.append(f"evidence[{index}].artifacts must be an array")
            continue
        for art_index, artifact in enumerate(artifacts):
            art = _as_object(
                artifact, f"evidence[{index}].artifacts[{art_index}]", errors
            )
            if art is None:
                continue
            path = art.get("path")
            if not isinstance(path, str) or not path.strip():
                errors.append(
                    f"evidence[{index}].artifacts[{art_index}].path is required"
                )
            elif "\\" in path or path.startswith("/") or ".." in Path(path).parts:
                errors.append(
                    f"evidence[{index}].artifacts[{art_index}].path must be relative POSIX"
                )
            if not str(art.get("kind") or "").strip():
                errors.append(
                    f"evidence[{index}].artifacts[{art_index}].kind is required"
                )

    if "hunt_plan" in facts and facts["hunt_plan"] is not None:
        errors.extend(_validate_hunt_plan_facts(facts["hunt_plan"]))
    return errors


def _validate_hunt_plan_facts(raw: Any) -> list[str]:
    if not isinstance(raw, dict):
        return ["hunt_plan must be an object"]
    try:
        plan = _hunt_plan_from_facts(raw)
    except (CheckpointError, hunt_plan.HuntPlanError) as exc:
        return [f"hunt_plan: {exc}"]
    return [f"hunt_plan: {item}" for item in hunt_plan.validate_hunt_plan(plan)]


def _hunt_plan_from_facts(raw: dict[str, Any]) -> hunt_plan.HuntPlan:
    surfaces = raw.get("surfaces") or {}
    if not isinstance(surfaces, dict):
        raise CheckpointError("hunt_plan.surfaces must be an object")
    bets_raw = raw.get("bets") or []
    if not isinstance(bets_raw, list):
        raise CheckpointError("hunt_plan.bets must be an array")
    bets: list[hunt_plan.Bet] = []
    for index, item in enumerate(bets_raw):
        if not isinstance(item, dict):
            raise CheckpointError(f"hunt_plan.bets[{index}] must be an object")
        bet_id = str(item.get("id") or "").strip()
        if not bet_id.startswith("H-"):
            raise CheckpointError(f"hunt_plan.bets[{index}].id must start with H-")
        try:
            rank = int(item.get("rank", 1))
        except (TypeError, ValueError) as exc:
            raise CheckpointError(
                f"hunt_plan.bets[{index}].rank must be an integer"
            ) from exc
        bets.append(
            hunt_plan.Bet(
                id=bet_id,
                rank=rank,
                claim=str(item.get("claim") or ""),
                probe=str(item.get("probe") or ""),
                expect=str(item.get("expect") or ""),
                kill_if=str(item.get("kill_if") or ""),
                status=str(item.get("status") or "active"),
            )
        )
    try:
        attempts = int(raw.get("attempts", 0))
    except (TypeError, ValueError) as exc:
        raise CheckpointError("hunt_plan.attempts must be an integer") from exc
    plan = hunt_plan.HuntPlan(
        phase=str(raw.get("phase") or "OBSERVE"),
        goal=str(raw.get("goal") or ""),
        have=str(raw.get("have") or ""),
        next_probe=str(raw.get("next_probe") or ""),
        attempts=attempts,
        untested=str(raw.get("untested") or ""),
        adjust=str(raw.get("adjust") or "stay"),
        wildcard=str(raw.get("wildcard") or ""),
        materials=str(raw.get("materials") or "none"),
        last_expected=str(raw.get("last_expected") or ""),
        last_observed=str(raw.get("last_observed") or ""),
        surfaces={
            name: str(surfaces.get(name) or "untested")
            for name in hunt_plan.SURFACE_CLASSES
        },
        bets=bets,
    )
    return plan


def _meta_comment(meta: dict[str, Any]) -> str:
    payload = json.dumps(meta, separators=(",", ":"), ensure_ascii=False)
    return f"<!-- huntboard-state: {payload} -->"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join("------" for _ in headers) + "|"
    body = ["| " + " | ".join(_cell(col) for col in row) + " |" for row in rows]
    return "\n".join([head, sep, *body]) if body else "\n".join([head, sep])


def render_files(facts: dict[str, Any], meta: dict[str, Any]) -> dict[str, str]:
    comment = _meta_comment(meta)
    assets = facts.get("assets") or []
    asset_rows = [
        [
            item["id"],
            item.get("label") or item.get("host") or "",
            item.get("kind") or "",
            item.get("address") or "",
            item.get("state") or "",
            item.get("notes") or "",
        ]
        for item in assets
    ]
    asset_graph = "\n".join(
        [
            "# Asset Graph",
            comment,
            "",
            _table(["ID", "物件", "種類", "位址／名", "狀態", "備註"], asset_rows),
            "",
        ]
    )

    route_rows = [
        [
            item["id"],
            item.get("name") or "",
            item.get("status") or "active",
            item.get("focus") or "",
        ]
        for item in (facts.get("routes") or [])
    ]
    active_hyps = [
        item
        for item in (facts.get("hypotheses") or [])
        if item.get("status", "active") == "active"
    ]
    numbered: list[str] = []
    for index, item in enumerate(active_hyps, start=1):
        priority = item.get("priority") or "HIGH"
        claim = _cell(item.get("claim") or "")
        probe = _cell(item.get("probe") or "")
        kill_if = _cell(item.get("kill_if") or "")
        extra = []
        if probe:
            extra.append(f"下一探：{probe}")
        if kill_if:
            extra.append(f"否證：{kill_if}")
        suffix = "。".join(extra)
        line = f"{index}. **[{item['id']}] [{priority}]** {claim}"
        if suffix:
            line = f"{line}。{suffix}。"
        numbered.append(line)

    closed_items = list(facts.get("closed") or [])
    closed_items.extend(
        item
        for item in (facts.get("hypotheses") or [])
        if item.get("status") in {"closed", "paused"}
    )
    closed_rows = [
        [
            item["id"],
            item.get("claim") or "",
            item.get("status") or "closed",
            item.get("reopen_if") or "",
        ]
        for item in closed_items
    ]
    route_parts = [
        "# Route Stack",
        comment,
        "",
        _table(["ID", "路線", "狀態", "焦點"], route_rows),
        "",
    ]
    if numbered:
        route_parts.extend(numbered)
        route_parts.append("")
    route_parts.extend(
        [
            "## Closed / Paused",
            "",
            _table(["ID", "主張", "狀態", "scoped reopen-if"], closed_rows),
            "",
        ]
    )
    route_stack = "\n".join(route_parts)

    loot_rows = [
        [
            item["id"],
            item.get("kind") or "",
            item.get("value") or "",
            item.get("source") or "",
            item.get("state") or "",
            item.get("use") or "",
        ]
        for item in (facts.get("loot") or [])
    ]
    loot_tracker = "\n".join(
        [
            "# Loot Tracker",
            comment,
            "",
            _table(["ID", "種類", "值／指標", "來源", "狀態", "使用"], loot_rows),
            "",
        ]
    )

    session = {
        **meta,
        "mode": facts["mode"],
        "scope": list(facts["scope"]),
        "targets": [
            {
                "id": item["id"],
                "ip": item["ip"],
                "hostname": item["hostname"],
                "status": item["status"],
            }
            for item in facts["targets"]
        ],
        "last_stop": dict(facts["last_stop"]),
    }
    evidence_doc = {
        **meta,
        "entries": list(facts.get("evidence") or []),
    }
    files = {
        "asset-graph.md": asset_graph,
        "route-stack.md": route_stack,
        "loot-tracker.md": loot_tracker,
        "session-index.json": json.dumps(session, ensure_ascii=False, indent=2)
        + "\n",
        "evidence-index.json": json.dumps(evidence_doc, ensure_ascii=False, indent=2)
        + "\n",
    }
    if facts.get("hunt_plan"):
        plan = _hunt_plan_from_facts(facts["hunt_plan"])
        files["hunt-plan.md"] = hunt_plan.render_hunt_plan(plan)
    return files


def write_checkpoint(
    root: Path,
    facts: dict[str, Any],
    *,
    checkpoint_id: str | None = None,
) -> load_state_bundle.BundleResult:
    errors = validate_facts(facts)
    if errors:
        raise CheckpointError("\n".join(errors))
    meta = {
        "schema_version": 2,
        "checkpoint_id": checkpoint_id
        or str(facts.get("checkpoint_id") or _new_checkpoint_id()),
        "last_updated": str(facts.get("last_updated") or _now_iso()),
    }
    files = render_files(facts, meta)
    root = root.expanduser()
    root.mkdir(parents=True, exist_ok=True)
    resolved_root = root.resolve()

    with tempfile.TemporaryDirectory(prefix="hs-checkpoint-") as tmp:
        tmp_path = Path(tmp)
        _stage_loot(resolved_root / "loot", tmp_path / "loot")
        for name, text in files.items():
            (tmp_path / name).write_text(text, encoding="utf-8")
        preview = load_state_bundle.load_bundle(tmp_path)
        if preview.status != 0:
            return preview
        for name, text in files.items():
            (resolved_root / name).write_text(text, encoding="utf-8")
    return load_state_bundle.load_bundle(resolved_root)


def _stage_loot(source: Path, dest: Path) -> None:
    if not source.exists():
        return

    def link_or_copy(src: str, dst: str, *, follow_symlinks: bool = True) -> str:
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        return dst

    shutil.copytree(source, dest, copy_function=link_or_copy, dirs_exist_ok=True)


def _load_facts(path: str) -> dict[str, Any]:
    if path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CheckpointError(f"facts JSON is invalid: {exc.msg} (line {exc.lineno})") from exc
    if not isinstance(data, dict):
        raise CheckpointError("facts JSON must be an object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Write pentest-state core files from one facts JSON. "
            "Validates before replacing any existing core file. "
            "Combat: one facts file, one run; on failure fix the JSON and run once more."
        )
    )
    parser.add_argument(
        "--facts",
        help="facts JSON path, or - for stdin",
    )
    parser.add_argument(
        "state_dir",
        nargs="?",
        default="./pentest-state",
        type=Path,
        help="state bundle directory (default: ./pentest-state)",
    )
    parser.add_argument(
        "--id",
        dest="checkpoint_id",
        default=None,
        help="checkpoint_id (default: cp-YYYYMMDD-HHMMSS)",
    )
    parser.add_argument(
        "--print-schema",
        action="store_true",
        help="print the facts JSON shape and exit",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="dump core file bodies after a successful write",
    )
    args = parser.parse_args(argv)
    if args.print_schema:
        sys.stdout.write(SCHEMA_EXAMPLE.strip() + "\n")
        return 0
    if not args.facts:
        parser.error("--facts is required unless --print-schema")
    try:
        facts = _load_facts(args.facts)
        result = write_checkpoint(
            args.state_dir, facts, checkpoint_id=args.checkpoint_id
        )
    except CheckpointError as exc:
        print(f"ERROR: facts rejected; state directory not changed\n{exc}", file=sys.stderr)
        return 1
    sys.stdout.write(result.render(full=args.full))
    if result.status != 0:
        print(
            "ERROR: generated bundle failed validation; original core files kept",
            file=sys.stderr,
        )
        for item in result.errors:
            print(f"ERROR: {item}", file=sys.stderr)
        for item in result.warnings:
            print(f"WARNING: {item}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
