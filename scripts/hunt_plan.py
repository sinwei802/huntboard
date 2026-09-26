#!/usr/bin/env python3
"""Hunt plan schema, phase machine, and stance-line codec.

Canonical field names and transition rules for huntspear. Semantics live in
``references/hunt-loop.md``. This module is the mechanical source of truth:
validate, adjust, and decide whether a deep act is allowed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Mapping


PHASES = ("OBSERVE", "DESIGN", "EXECUTE", "ADJUST", "SUCCESS")
SURFACE_CLASSES = ("transport", "identity_unauth", "naming", "materials")
SURFACE_STATES = ("seen", "oos", "untested")
MATERIALS_STATES = ("read", "deferred", "none", "unread")
BET_STATUSES = ("active", "killed", "paused")
REWIRE = (
    "stay",
    "next-bet",
    "re-observe",
    "re-design",
    "stall",
    "success",
)
ADJUST_OUTCOMES = (
    "fact_gained",
    "bet_killed",
    "new_surface",
    "unknown_primitive",
    "goal_achieved",
    "engagement_done",
)
DEEP_ACT_KINDS = ("exploit", "auth_use", "spray", "state_change", "pivot")
SHALLOW_ACT_KINDS = ("observe", "fingerprint", "read_local", "research")
OPENING_INTENTS = (
    "observe_transport",
    "observe_remainder_batch",
    "named_step",
)

# Compact HANDOFF line. One home for the rendered campaign card.
STANCE_PREFIX = "態勢："
_STANCE_TOKEN = re.compile(r"(Phase|Goal|主賭|下一探|attempts|未測軸|調整|HAVE|wildcard)=(.+?)(?=\s·\s[A-Za-z\u4e00-\u9fff]+=|$)")
_OPENING_RE = re.compile(r"開局|進行作戰|開始狩獵|開始打|先掃描|先掃")
_SCAN_RE = re.compile(r"掃描|掃一下|掃端口|掃埠|rustscan|nmap|(?:^|[\s，。])掃(?:[\s，。]|$)")


class HuntPlanError(ValueError):
    """Invalid hunt-plan document or transition."""


@dataclass
class Bet:
    id: str
    rank: int
    claim: str
    probe: str
    expect: str
    kill_if: str
    status: str = "active"

    def errors(self) -> list[str]:
        found: list[str] = []
        if not self.id.startswith("H-"):
            found.append(f"{self.id}: bet id must start with H-")
        if self.rank < 1:
            found.append(f"{self.id}: rank must be >= 1")
        if not self.claim.strip():
            found.append(f"{self.id}: claim is required")
        if not self.probe.strip():
            found.append(f"{self.id}: probe is required")
        if not self.expect.strip():
            found.append(f"{self.id}: expect is required")
        if not self.kill_if.strip():
            found.append(f"{self.id}: kill_if is required")
        if self.status not in BET_STATUSES:
            found.append(f"{self.id}: status must be one of {BET_STATUSES}")
        return found


@dataclass
class HuntPlan:
    phase: str = "OBSERVE"
    goal: str = ""
    have: str = ""
    next_probe: str = ""
    attempts: int = 0
    untested: str = ""
    adjust: str = "stay"
    wildcard: str = ""
    materials: str = "none"
    last_expected: str = ""
    last_observed: str = ""
    surfaces: dict[str, str] = field(
        default_factory=lambda: {name: "untested" for name in SURFACE_CLASSES}
    )
    bets: list[Bet] = field(default_factory=list)

    def copy(self) -> "HuntPlan":
        return HuntPlan(
            phase=self.phase,
            goal=self.goal,
            have=self.have,
            next_probe=self.next_probe,
            attempts=self.attempts,
            untested=self.untested,
            adjust=self.adjust,
            wildcard=self.wildcard,
            materials=self.materials,
            last_expected=self.last_expected,
            last_observed=self.last_observed,
            surfaces=dict(self.surfaces),
            bets=[
                Bet(
                    id=bet.id,
                    rank=bet.rank,
                    claim=bet.claim,
                    probe=bet.probe,
                    expect=bet.expect,
                    kill_if=bet.kill_if,
                    status=bet.status,
                )
                for bet in self.bets
            ],
        )


def observation_complete(plan: HuntPlan) -> bool:
    if not plan.have.strip():
        return False
    if plan.materials not in MATERIALS_STATES or plan.materials == "unread":
        return False
    for name in SURFACE_CLASSES:
        state = plan.surfaces.get(name, "untested")
        if state not in {"seen", "oos"}:
            return False
    return True


def observation_gaps(plan: HuntPlan) -> list[str]:
    gaps: list[str] = []
    if not plan.have.strip():
        gaps.append("have")
    if plan.materials == "unread" or plan.materials not in MATERIALS_STATES:
        gaps.append("materials")
    for name in SURFACE_CLASSES:
        if plan.surfaces.get(name, "untested") not in {"seen", "oos"}:
            gaps.append(f"surface.{name}")
    return gaps


def is_deep_act(kind: str) -> bool:
    if kind in DEEP_ACT_KINDS:
        return True
    if kind in SHALLOW_ACT_KINDS:
        return False
    raise HuntPlanError(
        f"unknown act kind {kind!r}; expected one of "
        f"{DEEP_ACT_KINDS + SHALLOW_ACT_KINDS}"
    )


def allows_design_search(plan: HuntPlan) -> bool:
    return observation_complete(plan) and plan.phase in {"OBSERVE", "DESIGN"}


def allows_deep_act(plan: HuntPlan, kind: str = "exploit") -> bool:
    if not is_deep_act(kind):
        return True
    if not observation_complete(plan):
        return False
    if plan.phase not in {"EXECUTE", "ADJUST"}:
        return False
    if not plan.goal.strip():
        return False
    if not plan.next_probe.strip():
        return False
    if not any(bet.status == "active" for bet in plan.bets):
        return False
    return True


def active_bets(plan: HuntPlan) -> list[Bet]:
    return sorted(
        (bet for bet in plan.bets if bet.status == "active"),
        key=lambda bet: bet.rank,
    )


def apply_adjust(plan: HuntPlan, outcome: str, observed: str) -> HuntPlan:
    if outcome not in ADJUST_OUTCOMES:
        raise HuntPlanError(
            f"unknown outcome {outcome!r}; expected one of {ADJUST_OUTCOMES}"
        )
    updated = plan.copy()
    updated.last_observed = observed
    updated.phase = "ADJUST"

    if outcome == "fact_gained":
        updated.attempts = 0
        updated.adjust = "stay"
        updated.phase = "EXECUTE"
        return updated

    if outcome == "bet_killed":
        current = next(iter(active_bets(updated)), None)
        if current is not None:
            current.status = "killed"
        nxt = next(iter(active_bets(updated)), None)
        if nxt is None:
            updated.adjust = "stall"
            updated.next_probe = ""
            updated.phase = "ADJUST"
        else:
            updated.adjust = "next-bet"
            updated.next_probe = nxt.probe
            updated.last_expected = nxt.expect
            updated.phase = "EXECUTE"
        return updated

    if outcome == "new_surface":
        updated.adjust = "re-observe"
        updated.phase = "OBSERVE"
        # A newly revealed class is untested until named seen/oos.
        for name in SURFACE_CLASSES:
            if updated.surfaces.get(name) == "oos":
                continue
            if updated.surfaces.get(name) != "seen":
                updated.surfaces[name] = "untested"
                break
        else:
            # All were seen; reopen materials so the new slice must be named.
            updated.surfaces["materials"] = "untested"
            updated.materials = "unread"
        return updated

    if outcome == "unknown_primitive":
        updated.adjust = "re-design"
        updated.phase = "DESIGN"
        return updated

    if outcome == "goal_achieved":
        updated.adjust = "re-design"
        updated.phase = "DESIGN"
        updated.attempts = 0
        updated.next_probe = ""
        return updated

    # engagement_done
    updated.adjust = "success"
    updated.phase = "SUCCESS"
    updated.next_probe = ""
    return updated


def parse_stance_line(text: str) -> dict[str, str]:
    line = text.strip()
    if "態勢：" in line:
        line = line[line.index("態勢：") :]
    if not line.startswith(STANCE_PREFIX):
        raise HuntPlanError("stance line must start with 態勢：")
    body = line[len(STANCE_PREFIX) :]
    fields = {key: value.strip() for key, value in _STANCE_TOKEN.findall(body)}
    if "Goal" not in fields:
        raise HuntPlanError("stance line missing Goal=")
    return fields


def render_stance_line(plan: HuntPlan) -> str:
    lead = active_bets(plan)
    primary = ""
    if lead:
        primary = f"{lead[0].id} {lead[0].claim}"
    parts = [
        f"Phase={plan.phase}",
        f"Goal={plan.goal or '（未定）'}",
        f"主賭={primary or '（無）'}",
        f"下一探={plan.next_probe or '（無）'}",
        f"attempts={plan.attempts}",
        f"未測軸={plan.untested or '（無）'}",
        f"調整={plan.adjust}",
    ]
    if plan.have.strip():
        parts.append(f"HAVE={plan.have}")
    if plan.wildcard.strip():
        parts.append(f"wildcard={plan.wildcard}")
    return STANCE_PREFIX + " · ".join(parts)


def stance_to_plan(fields: Mapping[str, str], base: HuntPlan | None = None) -> HuntPlan:
    plan = base.copy() if base is not None else HuntPlan()
    if "Phase" in fields and fields["Phase"] in PHASES:
        plan.phase = fields["Phase"]
    if "Goal" in fields:
        plan.goal = fields["Goal"]
    if "下一探" in fields and fields["下一探"] not in {"（無）", ""}:
        plan.next_probe = fields["下一探"]
    if "attempts" in fields:
        try:
            plan.attempts = int(fields["attempts"])
        except ValueError as exc:
            raise HuntPlanError("attempts must be an integer") from exc
    if "未測軸" in fields and fields["未測軸"] not in {"（無）", ""}:
        plan.untested = fields["未測軸"]
    if "調整" in fields and fields["調整"] in REWIRE:
        plan.adjust = fields["調整"]
    if "HAVE" in fields:
        plan.have = fields["HAVE"]
    if "wildcard" in fields and fields["wildcard"] not in {"（無）", ""}:
        plan.wildcard = fields["wildcard"]
    if "主賭" in fields and fields["主賭"] not in {"（無）", ""}:
        raw = fields["主賭"]
        bet_id, _, claim = raw.partition(" ")
        if bet_id.startswith("H-"):
            existing = next((bet for bet in plan.bets if bet.id == bet_id), None)
            if existing is None:
                plan.bets.append(
                    Bet(
                        id=bet_id,
                        rank=1,
                        claim=claim or raw,
                        probe=plan.next_probe,
                        expect="（從態勢列補）",
                        kill_if="（從態勢列補）",
                    )
                )
            else:
                if claim:
                    existing.claim = claim
    return plan


def parse_hunt_plan(text: str) -> HuntPlan:
    plan = HuntPlan()
    bets: dict[str, dict[str, str]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue
        if line.startswith("- "):
            line = line[2:]
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key.startswith("surface."):
            name = key.split(".", 1)[1]
            if name not in SURFACE_CLASSES:
                raise HuntPlanError(f"unknown surface class {name!r}")
            if value not in SURFACE_STATES:
                raise HuntPlanError(f"surface.{name} must be one of {SURFACE_STATES}")
            plan.surfaces[name] = value
            continue
        if key.startswith("bet."):
            _, bet_id, field_name = _split_bet_key(key)
            bets.setdefault(bet_id, {})[field_name] = value
            continue
        _assign_scalar(plan, key, value)
    plan.bets = [_bet_from_fields(bet_id, fields) for bet_id, fields in bets.items()]
    plan.bets.sort(key=lambda bet: (bet.rank, bet.id))
    return plan


def render_hunt_plan(plan: HuntPlan) -> str:
    lines = ["# Hunt Plan", ""]
    scalars = (
        ("phase", plan.phase),
        ("goal", plan.goal),
        ("have", plan.have),
        ("next_probe", plan.next_probe),
        ("attempts", str(plan.attempts)),
        ("untested", plan.untested),
        ("adjust", plan.adjust),
        ("wildcard", plan.wildcard),
        ("materials", plan.materials),
        ("last_expected", plan.last_expected),
        ("last_observed", plan.last_observed),
    )
    for key, value in scalars:
        lines.append(f"{key}: {value}")
    lines.append("")
    for name in SURFACE_CLASSES:
        lines.append(f"surface.{name}: {plan.surfaces.get(name, 'untested')}")
    lines.append("")
    for bet in plan.bets:
        lines.append(f"bet.{bet.id}.rank: {bet.rank}")
        lines.append(f"bet.{bet.id}.claim: {bet.claim}")
        lines.append(f"bet.{bet.id}.probe: {bet.probe}")
        lines.append(f"bet.{bet.id}.expect: {bet.expect}")
        lines.append(f"bet.{bet.id}.kill_if: {bet.kill_if}")
        lines.append(f"bet.{bet.id}.status: {bet.status}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def validate_hunt_plan(plan: HuntPlan) -> list[str]:
    errors: list[str] = []
    if plan.phase not in PHASES:
        errors.append(f"phase must be one of {PHASES}")
    if plan.adjust not in REWIRE:
        errors.append(f"adjust must be one of {REWIRE}")
    if plan.materials not in MATERIALS_STATES:
        errors.append(f"materials must be one of {MATERIALS_STATES}")
    if plan.attempts < 0:
        errors.append("attempts must be >= 0")
    for name in SURFACE_CLASSES:
        state = plan.surfaces.get(name)
        if state not in SURFACE_STATES:
            errors.append(f"surface.{name} must be one of {SURFACE_STATES}")
    for bet in plan.bets:
        errors.extend(bet.errors())
    if plan.phase in {"EXECUTE", "SUCCESS"} and not observation_complete(plan):
        errors.append(
            "phase "
            + plan.phase
            + " requires complete observation; missing "
            + ",".join(observation_gaps(plan))
        )
    if plan.phase == "EXECUTE":
        if not plan.goal.strip():
            errors.append("EXECUTE requires goal")
        if not plan.next_probe.strip():
            errors.append("EXECUTE requires next_probe")
        if not any(bet.status == "active" for bet in plan.bets):
            errors.append("EXECUTE requires at least one active bet")
    if plan.phase == "SUCCESS" and plan.adjust != "success":
        errors.append("SUCCESS requires adjust=success")
    return errors


def opening_intent(
    text: str,
    *,
    ports_known: bool,
    observe_complete_flag: bool,
) -> str:
    """Map an opening utterance to a campaign intent.

    Does not authorize exploit. Transport vs remainder is split so the first
    scan's derived ports are not used in the same STEP (R1).
    """
    if observe_complete_flag:
        return "named_step"
    opening = bool(_OPENING_RE.search(text))
    scan = bool(_SCAN_RE.search(text))
    if not opening and not scan:
        return "named_step"
    if not ports_known:
        return "observe_transport"
    return "observe_remainder_batch"


def load_hunt_plan(path: Path) -> HuntPlan:
    return parse_hunt_plan(path.read_text(encoding="utf-8"))


def _split_bet_key(key: str) -> tuple[str, str, str]:
    parts = key.split(".")
    if len(parts) != 3:
        raise HuntPlanError(f"bet key must be bet.<id>.<field>, got {key!r}")
    return parts[0], parts[1], parts[2]


def _bet_from_fields(bet_id: str, fields: Mapping[str, str]) -> Bet:
    try:
        rank = int(fields.get("rank", "1"))
    except ValueError as exc:
        raise HuntPlanError(f"{bet_id}: rank must be an integer") from exc
    return Bet(
        id=bet_id,
        rank=rank,
        claim=fields.get("claim", ""),
        probe=fields.get("probe", ""),
        expect=fields.get("expect", ""),
        kill_if=fields.get("kill_if", ""),
        status=fields.get("status", "active"),
    )


def _assign_scalar(plan: HuntPlan, key: str, value: str) -> None:
    if key == "phase":
        if value not in PHASES:
            raise HuntPlanError(f"phase must be one of {PHASES}")
        plan.phase = value
        return
    if key == "goal":
        plan.goal = value
        return
    if key == "have":
        plan.have = value
        return
    if key == "next_probe":
        plan.next_probe = value
        return
    if key == "attempts":
        try:
            plan.attempts = int(value)
        except ValueError as exc:
            raise HuntPlanError("attempts must be an integer") from exc
        return
    if key == "untested":
        plan.untested = value
        return
    if key == "adjust":
        if value not in REWIRE:
            raise HuntPlanError(f"adjust must be one of {REWIRE}")
        plan.adjust = value
        return
    if key == "wildcard":
        plan.wildcard = value
        return
    if key == "materials":
        if value not in MATERIALS_STATES:
            raise HuntPlanError(f"materials must be one of {MATERIALS_STATES}")
        plan.materials = value
        return
    if key == "last_expected":
        plan.last_expected = value
        return
    if key == "last_observed":
        plan.last_observed = value
        return
    raise HuntPlanError(f"unknown hunt-plan field {key!r}")


def _cmd_validate(path: Path) -> int:
    plan = load_hunt_plan(path)
    errors = validate_hunt_plan(plan)
    if errors:
        for item in errors:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print(f"OK phase={plan.phase} deep_act={allows_deep_act(plan)}")
    print(render_stance_line(plan))
    return 0


def _cmd_adjust(path: Path, outcome: str, observed: str, write: bool) -> int:
    plan = load_hunt_plan(path)
    updated = apply_adjust(plan, outcome, observed)
    errors = validate_hunt_plan(updated)
    sys.stdout.write(render_hunt_plan(updated))
    print(render_stance_line(updated), file=sys.stderr)
    if write:
        path.write_text(render_hunt_plan(updated), encoding="utf-8")
    if errors and updated.phase != "ADJUST":
        for item in errors:
            print(f"WARNING: {item}", file=sys.stderr)
    return 0


_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_REF_NAME_RE = re.compile(r"^[a-z0-9-]+(?:/[a-z0-9-]+)?$")
_SESSION_ID_ENV = (
    "HUNTSPEAR_SESSION_ID",
    # Keep reading the pre-rename variable so existing sessions continue to load.
    "HUNTBOARD_SESSION_ID",
    "GROK_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)


def _skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def session_id() -> str | None:
    for key in _SESSION_ID_ENV:
        value = os.environ.get(key, "").strip()
        if _SESSION_ID_RE.fullmatch(value):
            return value
    return None


def session_load_dir() -> Path:
    for key in ("HUNTSPEAR_SESSION_LOAD_DIR", "HUNTBOARD_SESSION_LOAD_DIR"):
        override = os.environ.get(key, "").strip()
        if override:
            return Path(override)
    current = Path.home() / ".cache" / "huntspear" / "session-load"
    legacy = Path.home() / ".cache" / "huntboard" / "session-load"
    if legacy.exists() and not current.exists():
        return legacy
    return current


def _reference_path(name: str) -> Path:
    if not _REF_NAME_RE.fullmatch(name):
        raise HuntPlanError(f"unknown reference {name}")
    path = _skill_root() / "references" / f"{name}.md"
    if not path.is_file():
        raise HuntPlanError(f"unknown reference {name}")
    return path


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _session_load_path(sid: str) -> Path:
    return session_load_dir() / f"{sid}.json"


def _read_session_record() -> dict[str, dict[str, str]]:
    sid = session_id()
    if sid is None:
        return {}
    path = _session_load_path(sid)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if data.get("session") != sid:
        return {}
    loaded = data.get("loaded")
    if not isinstance(loaded, dict):
        return {}
    clean: dict[str, dict[str, str]] = {}
    for name, meta in loaded.items():
        if not isinstance(name, str) or not isinstance(meta, dict):
            continue
        digest = meta.get("sha256")
        if isinstance(digest, str):
            clean[name] = {"sha256": digest}
    return clean


def session_load_status() -> tuple[list[str], list[str]]:
    """Return (fresh short names, stale short names) for this conversation."""
    if session_id() is None:
        return [], []
    fresh: list[str] = []
    stale: list[str] = []
    for name, meta in _read_session_record().items():
        try:
            current = _file_sha256(_reference_path(name))
        except (HuntPlanError, OSError):
            stale.append(name)
            continue
        if meta.get("sha256") == current:
            fresh.append(name)
        else:
            stale.append(name)
    fresh.sort()
    stale.sort()
    return fresh, stale


def format_loaded_line() -> str:
    if session_id() is None:
        return "loaded= session=absent"
    fresh, stale = session_load_status()
    line = "loaded=" + ",".join(fresh)
    if stale:
        line += " stale=" + ",".join(stale)
    return line


def mark_session_load(names: list[str]) -> str:
    sid = session_id()
    if sid is None:
        return "session=absent"
    if not names:
        raise HuntPlanError("session-load mark needs at least one reference short name")
    record = _read_session_record()
    marked_at = datetime.now().astimezone().isoformat(timespec="seconds")
    for name in names:
        record[name] = {
            "sha256": _file_sha256(_reference_path(name)),
            "marked_at": marked_at,
        }
    path = _session_load_path(sid)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"session": sid, "loaded": record}
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return format_loaded_line()


def reset_session_load() -> str:
    sid = session_id()
    if sid is None:
        return "session=absent"
    path = _session_load_path(sid)
    if path.is_file():
        path.unlink()
    return "loaded="


def _cmd_opening(text: str, ports_known: bool, observe_done: bool) -> int:
    intent = opening_intent(
        text,
        ports_known=ports_known,
        observe_complete_flag=observe_done,
    )
    print(intent)
    print(format_loaded_line())
    return 0


def _cmd_session_load(cmd: str, names: list[str]) -> int:
    try:
        if cmd == "show":
            print(format_loaded_line())
            return 0
        if cmd == "mark":
            print(mark_session_load(names))
            return 0
        if cmd == "reset":
            print(reset_session_load())
            return 0
    except HuntPlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"ERROR: unknown session-load command {cmd}", file=sys.stderr)
    return 2


def _cmd_allows_deep(path: Path, kind: str) -> int:
    plan = load_hunt_plan(path)
    allowed = allows_deep_act(plan, kind)
    print("yes" if allowed else "no")
    if not allowed:
        for gap in observation_gaps(plan):
            print(f"gap:{gap}")
        if plan.phase not in {"EXECUTE", "ADJUST"}:
            print(f"gap:phase={plan.phase}")
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hunt plan phase machine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    validate = sub.add_parser("validate", help="validate a hunt-plan.md")
    validate.add_argument("path", type=Path)

    adjust = sub.add_parser("adjust", help="apply an adjust outcome and print the new plan")
    adjust.add_argument("path", type=Path)
    adjust.add_argument("--outcome", required=True, choices=ADJUST_OUTCOMES)
    adjust.add_argument("--observed", required=True)
    adjust.add_argument(
        "--write",
        action="store_true",
        help="overwrite the plan file with the adjusted plan",
    )

    opening = sub.add_parser("opening", help="classify an opening utterance")
    opening.add_argument("text")
    opening.add_argument("--ports-known", action="store_true")
    opening.add_argument("--observe-complete", action="store_true")

    session = sub.add_parser(
        "session-load",
        help="record which references this conversation already read",
    )
    session_sub = session.add_subparsers(dest="session_cmd", required=True)
    session_sub.add_parser("show", help="print loaded= and stale=")
    mark = session_sub.add_parser("mark", help="record reference short names")
    mark.add_argument("names", nargs="+")
    session_sub.add_parser("reset", help="forget the loaded list for this conversation")

    deep = sub.add_parser("allows-deep", help="exit 0 if a deep act is allowed")
    deep.add_argument("path", type=Path)
    deep.add_argument("--kind", default="exploit", choices=DEEP_ACT_KINDS + SHALLOW_ACT_KINDS)

    stance = sub.add_parser("render-stance", help="render the compact 態勢 line")
    stance.add_argument("path", type=Path)

    args = parser.parse_args(argv)
    if args.cmd == "validate":
        return _cmd_validate(args.path)
    if args.cmd == "adjust":
        return _cmd_adjust(args.path, args.outcome, args.observed, args.write)
    if args.cmd == "opening":
        return _cmd_opening(args.text, args.ports_known, args.observe_complete)
    if args.cmd == "session-load":
        return _cmd_session_load(args.session_cmd, getattr(args, "names", []))
    if args.cmd == "allows-deep":
        return _cmd_allows_deep(args.path, args.kind)
    if args.cmd == "render-stance":
        plan = load_hunt_plan(args.path)
        print(render_stance_line(plan))
        return 0
    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
