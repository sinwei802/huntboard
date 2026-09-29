#!/usr/bin/env python3
"""Validate a next-cut proposal against local-sense required fields.

Methodology gate only — no exploit content. Exit 0 = pass, 1 = fail, 2 = usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = (
    "phase",
    "hypothesis",
    "evidence_gate",
    "dead_if",
    "card_id",
    "cloud_cross",
)

PHASES = frozenset({"orient", "map", "probe", "decide", "idle"})

# Action classes that require a full open gate (not GAP:no-local-playbook)
HIGH_RISK = frozenset(
    {
        "exploit",
        "auth_use",
        "spray",
        "pivot",
        "poc",
        "brute",
        "persist",
    }
)

ACTIVE_CLOUD_IDS = frozenset(
    {
        "src-nvd",
        "src-vendor-adv",
        "src-rfc-mdn",
        "src-cisa-kev",
        "src-websearch",
        "src-mqtt-oasis",
    }
)

KNOWN_CARDS = frozenset(
    {
        "http-observe-only",
        "evidence-gate",
        "dead-path-mark",
        "public-doc-cve-lookup",
        "local-sense-memory",
        "post-foothold-map",
        "priv-esc-evidence-gate",
        "web-app-evidence-ladder",
        "challenge-board-handoff",
        "session-break-rebuild",
        "owner-root-flag-bar",
        "doctrine-compatible-privesc",
        "post-engagement-retro",
        "GAP:no-local-playbook",
    }
)


def _as_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return []


def check(proposal: dict[str, Any]) -> list[str]:
    """Return list of failure reasons (empty = pass)."""
    errs: list[str] = []

    for key in REQUIRED:
        if key not in proposal or proposal[key] in (None, "", []):
            errs.append(f"missing:{key}")

    phase = str(proposal.get("phase", "")).strip().lower()
    if phase and phase not in PHASES:
        errs.append(f"bad_phase:{phase}")

    hyp = str(proposal.get("hypothesis", "")).strip()
    if hyp and len(hyp) < 8:
        errs.append("hypothesis:too_short")

    eg = str(proposal.get("evidence_gate", "")).strip()
    if eg and ("感覺" in eg or eg.lower() in {"ok", "yes", "看起來可以"}):
        errs.append("evidence_gate:not_concrete")

    card = str(proposal.get("card_id", "")).strip()
    if card and card not in KNOWN_CARDS:
        errs.append(f"unknown_card:{card}")

    cloud = _as_list(proposal.get("cloud_cross"))
    if "missing:cloud_cross" not in errs:
        if len(cloud) < 2:
            errs.append("cloud_cross:need_ge_2")
        else:
            unknown = [c for c in cloud if c not in ACTIVE_CLOUD_IDS]
            if unknown:
                errs.append("cloud_cross:unknown:" + ",".join(unknown))
            # watch-only sources are not in ACTIVE — already caught as unknown

    action = str(proposal.get("action_class", "observe")).strip().lower()
    if action in HIGH_RISK:
        if card == "GAP:no-local-playbook":
            errs.append("high_risk_blocked:GAP:no-local-playbook")
        if any(e.startswith("missing:") for e in errs):
            errs.append("high_risk_requires_full_sense")

    return errs


def _db_errors(db: Path, action: str) -> list[str]:
    scripts = Path(__file__).resolve().parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import warboard

    return warboard.gate_action(db, action)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Local-sense proposal gate")
    p.add_argument(
        "--check",
        metavar="FILE",
        help="JSON proposal file to validate",
    )
    p.add_argument(
        "--db",
        metavar="SQLITE",
        help="warboard sqlite; high-risk gates read the db, not the proposal",
    )
    p.add_argument(
        "--action",
        default=None,
        help="action class for --db gates (default: proposal action_class or observe)",
    )
    p.add_argument(
        "--print-schema",
        action="store_true",
        help="Print required fields and exit 0",
    )
    args = p.parse_args(argv)

    if args.print_schema:
        print(
            json.dumps(
                {
                    "required": list(REQUIRED),
                    "phases": sorted(PHASES),
                    "high_risk_action_class": sorted(HIGH_RISK),
                    "active_cloud_ids": sorted(ACTIVE_CLOUD_IDS),
                    "known_card_ids": sorted(KNOWN_CARDS),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    data: dict[str, Any] | None = None
    if args.check:
        path = Path(args.check)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"FAIL read:{e}", file=sys.stderr)
            return 1
        if not isinstance(loaded, dict):
            print("FAIL not_object", file=sys.stderr)
            return 1
        data = loaded

    if data is None and not args.db:
        p.print_help()
        return 2

    errs: list[str] = []
    if data is not None:
        errs.extend(check(data))

    action = (args.action or "").strip().lower()
    if not action and data is not None:
        action = str(data.get("action_class") or "observe").strip().lower()
    if not action:
        action = "observe"

    if args.db:
        errs.extend(_db_errors(Path(args.db), action))

    if errs:
        print("FAIL " + " ".join(errs), file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
