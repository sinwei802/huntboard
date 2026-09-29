#!/usr/bin/env python3
"""Warboard SQLite runtime — sole engagement truth.

Markdown pentest-state core files are debt. This module never reads them as
HAVE and never writes them. Exit 0 = ok, 1 = rejected facts, 2 = usage.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import hunt_plan  # noqa: E402

SCHEMA_SQL = _SCRIPTS / "warboard_schema.sql"
DEFAULT_STATE_ROOT = Path("./pentest-state")
DB_NAME = "warboard.sqlite"
MARKDOWN_DEBT = (
    "session-index.json",
    "asset-graph.md",
    "route-stack.md",
    "loot-tracker.md",
    "evidence-index.json",
    "hunt-plan.md",
)
HIGH_RISK = frozenset(
    {"exploit", "auth_use", "spray", "pivot", "poc", "brute", "persist"}
)
SECRET_ACTIONS = frozenset({"auth_use", "spray", "brute", "poc"})
SENSITIVE_LOOT = frozenset({"credential", "hash", "token", "ticket"})
OBSERVED_SURFACE = frozenset({"seen", "fingerprinted", "interesting"})
CAMPAIGN_OK = frozenset({"seen", "oos"})

FACTS_SCHEMA = {
    "engagement": {
        "name": "lab",
        "mode": "ctf",
        "scope_notes": "10.10.11.1",
    },
    "assets": [
        {
            "id": "A-1",
            "address": "10.10.11.1",
            "hostname": "target",
            "status": "reachable",
        }
    ],
    "surfaces": [
        {
            "id": "S-1",
            "asset_id": "A-1",
            "kind": "tcp",
            "port": 80,
            "status": "seen",
        }
    ],
    "identities": [
        {
            "id": "I-1",
            "label": "anonymous",
            "kind": "anonymous",
            "privilege_band": "none",
        }
    ],
    "loot": [
        {
            "id": "L-1",
            "kind": "hash",
            "sensitivity": "high",
            "label": "asrep-svc",
            "storage_ref": "loot/svc.asrep",
        }
    ],
    "hypotheses": [
        {
            "id": "H-1",
            "claim": "未認證目錄可列",
            "status": "open",
            "expect": "namingContexts",
            "kill_if": "LDAP 不可達",
            "probe": "LDAP rootDSE",
        }
    ],
    "goals": [
        {
            "id": "G-1",
            "title": "取得具名身份",
            "status": "active",
        }
    ],
    "focus": {
        "phase": "map",
        "summary": "transport seen",
        "active_asset_id": "A-1",
        "active_goal_id": "G-1",
    },
    "campaign": {
        "have": "anonymous http",
        "materials": "none",
        "next_probe": "LDAP rootDSE",
        "goal": "取得具名身份",
        "phase": "EXECUTE",
        "campaign_surfaces": {
            "transport": "seen",
            "identity_unauth": "seen",
            "naming": "seen",
            "materials": "seen",
        },
    },
}


class WarboardError(ValueError):
    """Invalid facts or missing database."""


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def db_path_for(state_root: Path) -> Path:
    return state_root / DB_NAME


def markdown_debt_names(state_root: Path) -> list[str]:
    found: list[str] = []
    for name in MARKDOWN_DEBT:
        if (state_root / name).is_file():
            found.append(name)
    return found


def connect(path: Path, *, create: bool) -> sqlite3.Connection:
    path = path.expanduser()
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    elif not path.is_file():
        raise WarboardError(f"db_missing:{path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if create:
        _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='engagements'"
    ).fetchone()
    if row:
        return
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _campaign_default() -> dict[str, Any]:
    return {
        "have": "",
        "materials": "none",
        "next_probe": "",
        "goal": "",
        "phase": "OBSERVE",
        "attempts": 0,
        "untested": "",
        "adjust": "stay",
        "wildcard": "",
        "last_expected": "",
        "last_observed": "",
        "campaign_surfaces": {
            name: "untested" for name in hunt_plan.SURFACE_CLASSES
        },
    }


def _parse_campaign(raw: str | None) -> dict[str, Any]:
    data = _campaign_default()
    if not raw:
        return data
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return data
    if not isinstance(parsed, dict):
        return data
    campaign = parsed.get("campaign") if isinstance(parsed.get("campaign"), dict) else parsed
    if not isinstance(campaign, dict):
        return data
    for key in (
        "have",
        "materials",
        "next_probe",
        "goal",
        "phase",
        "untested",
        "adjust",
        "wildcard",
        "last_expected",
        "last_observed",
    ):
        if key in campaign and campaign[key] is not None:
            data[key] = campaign[key]
    if "attempts" in campaign:
        try:
            data["attempts"] = int(campaign["attempts"])
        except (TypeError, ValueError):
            pass
    surfaces = campaign.get("campaign_surfaces")
    if isinstance(surfaces, dict):
        for name in hunt_plan.SURFACE_CLASSES:
            if name in surfaces:
                data["campaign_surfaces"][name] = str(surfaces[name])
    return data


def _dump_pending(campaign: dict[str, Any]) -> str:
    return json.dumps({"campaign": campaign}, ensure_ascii=False)


def active_engagement(conn: sqlite3.Connection) -> sqlite3.Row | None:
    row = conn.execute(
        "SELECT * FROM engagements WHERE status='active' "
        "ORDER BY updated_at DESC LIMIT 1"
    ).fetchone()
    if row:
        return row
    return conn.execute(
        "SELECT * FROM engagements ORDER BY updated_at DESC LIMIT 1"
    ).fetchone()


def ensure_engagement(
    conn: sqlite3.Connection,
    *,
    fresh: bool = False,
    name: str = "engagement",
    mode: str = "ctf",
    scope_notes: str | None = None,
) -> str:
    existing = active_engagement(conn)
    if existing and not fresh:
        return str(existing["id"])
    if existing and fresh:
        conn.execute(
            "UPDATE engagements SET status='paused', updated_at=? WHERE id=?",
            (now_iso(), existing["id"]),
        )
    eid = _new_id("E")
    ts = now_iso()
    if mode not in {"ctf", "pentest", "other"}:
        raise WarboardError(f"bad_mode:{mode}")
    conn.execute(
        "INSERT INTO engagements(id, name, status, mode, scope_notes, created_at, updated_at) "
        "VALUES (?, ?, 'active', ?, ?, ?, ?)",
        (eid, name, mode, scope_notes, ts, ts),
    )
    realm_id = _new_id("RLM")
    conn.execute(
        "INSERT INTO realms(id, engagement_id, name, kind, notes, created_at) "
        "VALUES (?, ?, 'default', 'lab', NULL, ?)",
        (realm_id, eid, ts),
    )
    conn.execute(
        "INSERT INTO focus(id, engagement_id, phase, summary, active_asset_id, "
        "active_goal_id, pending_decision_json, updated_at) "
        "VALUES (?, ?, 'orient', '', NULL, NULL, ?, ?)",
        (_new_id("F"), eid, _dump_pending(_campaign_default()), ts),
    )
    return eid


def default_realm_id(conn: sqlite3.Connection, engagement_id: str) -> str:
    row = conn.execute(
        "SELECT id FROM realms WHERE engagement_id=? ORDER BY created_at LIMIT 1",
        (engagement_id,),
    ).fetchone()
    if row:
        return str(row["id"])
    rid = _new_id("RLM")
    conn.execute(
        "INSERT INTO realms(id, engagement_id, name, kind, notes, created_at) "
        "VALUES (?, ?, 'default', 'lab', NULL, ?)",
        (rid, engagement_id, now_iso()),
    )
    return rid


def start_round(conn: sqlite3.Connection, engagement_id: str) -> int:
    n = current_round(conn, engagement_id) + 1
    conn.execute(
        "INSERT INTO events(id, engagement_id, kind, body_json, actor, "
        "related_focus_id, created_at) VALUES (?, ?, 'note', ?, 'system', NULL, ?)",
        (
            _new_id("EV"),
            engagement_id,
            json.dumps({"op": "round_start", "n": n}, ensure_ascii=False),
            now_iso(),
        ),
    )
    return n


def current_round(conn: sqlite3.Connection, engagement_id: str) -> int:
    rows = conn.execute(
        "SELECT body_json FROM events WHERE engagement_id=? AND kind='note' "
        "ORDER BY created_at",
        (engagement_id,),
    ).fetchall()
    last = 0
    for row in rows:
        try:
            body = json.loads(row["body_json"])
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict) and body.get("op") == "round_start":
            try:
                last = max(last, int(body.get("n", 0)))
            except (TypeError, ValueError):
                continue
    return last


def load_campaign(conn: sqlite3.Connection, engagement_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT pending_decision_json FROM focus WHERE engagement_id=?",
        (engagement_id,),
    ).fetchone()
    if not row:
        return _campaign_default()
    return _parse_campaign(row["pending_decision_json"])


def save_campaign(
    conn: sqlite3.Connection, engagement_id: str, campaign: dict[str, Any]
) -> None:
    ts = now_iso()
    payload = _dump_pending(campaign)
    row = conn.execute(
        "SELECT id FROM focus WHERE engagement_id=?", (engagement_id,)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE focus SET pending_decision_json=?, updated_at=? WHERE engagement_id=?",
            (payload, ts, engagement_id),
        )
        return
    conn.execute(
        "INSERT INTO focus(id, engagement_id, phase, summary, active_asset_id, "
        "active_goal_id, pending_decision_json, updated_at) "
        "VALUES (?, ?, 'orient', '', NULL, NULL, ?, ?)",
        (_new_id("F"), engagement_id, payload, ts),
    )


def observed_surface_count(conn: sqlite3.Connection, engagement_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM surfaces WHERE engagement_id=? AND status IN "
        "('seen','fingerprinted','interesting')",
        (engagement_id,),
    ).fetchone()
    return int(row["n"] if row else 0)


def open_hypothesis_count(conn: sqlite3.Connection, engagement_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM hypotheses WHERE engagement_id=? AND status='open'",
        (engagement_id,),
    ).fetchone()
    return int(row["n"] if row else 0)


def _round_started_at(conn: sqlite3.Connection, engagement_id: str) -> str | None:
    rows = conn.execute(
        "SELECT created_at, body_json FROM events WHERE engagement_id=? AND kind='note' "
        "ORDER BY created_at DESC",
        (engagement_id,),
    ).fetchall()
    for row in rows:
        try:
            body = json.loads(row["body_json"])
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict) and body.get("op") == "round_start":
            return str(row["created_at"])
    return None


def same_round_sensitive_loot(conn: sqlite3.Connection, engagement_id: str) -> bool:
    started = _round_started_at(conn, engagement_id)
    if not started:
        return False
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM loot WHERE engagement_id=? AND kind IN "
        "('credential','hash','token','ticket') AND created_at>=?",
        (engagement_id, started),
    ).fetchone()
    return int(row["n"] if row else 0) > 0


def gate_action(db: Path, action: str) -> list[str]:
    """Read-only high-risk gates. Empty list = pass. Does not trust a proposal."""
    action = action.strip().lower()
    if not db.is_file():
        if action in HIGH_RISK:
            return ["db_missing"]
        return []
    conn = connect(db, create=False)
    try:
        eng = active_engagement(conn)
        if eng is None:
            return ["h1_no_surface", "h2_no_bet"] if action in HIGH_RISK else []
        if action not in HIGH_RISK:
            return []
        eid = str(eng["id"])
        errs: list[str] = []
        campaign = load_campaign(conn, eid)
        if not str(campaign.get("have", "")).strip():
            errs.append("h1_no_have")
        if campaign.get("materials") == "unread":
            errs.append("h1_materials_unread")
        camp_sur = campaign.get("campaign_surfaces") or {}
        for name in hunt_plan.SURFACE_CLASSES:
            state = str(camp_sur.get(name, "untested"))
            if state not in CAMPAIGN_OK:
                errs.append(f"h1_surface_{name}")
        transport_ok = str(camp_sur.get("transport", "untested")) in CAMPAIGN_OK
        if observed_surface_count(conn, eid) == 0 and not transport_ok:
            errs.append("h1_no_surface")
        if open_hypothesis_count(conn, eid) == 0:
            errs.append("h2_no_bet")
        if not str(campaign.get("goal", "")).strip():
            errs.append("h2_no_goal")
        if not str(campaign.get("next_probe", "")).strip():
            errs.append("h2_no_next_probe")
        if action in SECRET_ACTIONS and same_round_sensitive_loot(conn, eid):
            errs.append("r2_same_round_secret")
        return errs
    finally:
        conn.close()


def _upsert_asset(
    conn: sqlite3.Connection, engagement_id: str, realm_id: str, item: dict[str, Any]
) -> str:
    aid = str(item.get("id") or _new_id("A"))
    hostname = item.get("hostname")
    address = item.get("address")
    if not hostname and not address:
        raise WarboardError(f"asset {aid}: hostname or address required")
    status = str(item.get("status") or "unknown")
    ts = now_iso()
    row = conn.execute("SELECT id FROM assets WHERE id=?", (aid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE assets SET hostname=?, address=?, status=?, os_guess=?, notes=?, "
            "updated_at=? WHERE id=?",
            (
                hostname,
                address,
                status,
                item.get("os_guess"),
                item.get("notes"),
                ts,
                aid,
            ),
        )
        return aid
    conn.execute(
        "INSERT INTO assets(id, engagement_id, realm_id, hostname, address, status, "
        "os_guess, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            aid,
            engagement_id,
            realm_id,
            hostname,
            address,
            status,
            item.get("os_guess"),
            item.get("notes"),
            ts,
            ts,
        ),
    )
    return aid


def _upsert_surface(
    conn: sqlite3.Connection, engagement_id: str, item: dict[str, Any]
) -> str:
    sid = str(item.get("id") or _new_id("S"))
    asset_id = item.get("asset_id")
    if not asset_id:
        raise WarboardError(f"surface {sid}: asset_id required")
    ts = now_iso()
    kind = str(item.get("kind") or "tcp")
    status = str(item.get("status") or "unseen")
    row = conn.execute("SELECT id FROM surfaces WHERE id=?", (sid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE surfaces SET kind=?, port=?, path_or_name=?, banner_or_product=?, "
            "status=?, notes=?, updated_at=? WHERE id=?",
            (
                kind,
                item.get("port"),
                item.get("path_or_name"),
                item.get("banner_or_product"),
                status,
                item.get("notes"),
                ts,
                sid,
            ),
        )
        return sid
    conn.execute(
        "INSERT INTO surfaces(id, asset_id, engagement_id, kind, port, path_or_name, "
        "banner_or_product, status, notes, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            sid,
            asset_id,
            engagement_id,
            kind,
            item.get("port"),
            item.get("path_or_name"),
            item.get("banner_or_product"),
            status,
            item.get("notes"),
            ts,
            ts,
        ),
    )
    return sid


def _insert_loot(
    conn: sqlite3.Connection, engagement_id: str, item: dict[str, Any]
) -> str:
    lid = str(item.get("id") or _new_id("L"))
    kind = str(item.get("kind") or "other")
    if kind not in SENSITIVE_LOOT | {"file", "note", "other"}:
        raise WarboardError(f"loot {lid}: bad kind {kind}")
    sensitivity = str(item.get("sensitivity") or "medium")
    label = str(item.get("label") or "").strip()
    if not label:
        raise WarboardError(f"loot {lid}: label required")
    storage_ref = item.get("storage_ref")
    if storage_ref and (str(storage_ref).startswith("/") or ".." in str(storage_ref)):
        raise WarboardError(f"loot {lid}: storage_ref must be relative")
    ts = now_iso()
    row = conn.execute("SELECT id FROM loot WHERE id=?", (lid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE loot SET kind=?, sensitivity=?, label=?, storage_ref=?, notes=? "
            "WHERE id=?",
            (kind, sensitivity, label, storage_ref, item.get("notes"), lid),
        )
        return lid
    conn.execute(
        "INSERT INTO loot(id, engagement_id, kind, sensitivity, label, storage_ref, "
        "source_asset_id, source_surface_id, identity_id, notes, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            lid,
            engagement_id,
            kind,
            sensitivity,
            label,
            storage_ref,
            item.get("source_asset_id"),
            item.get("source_surface_id"),
            item.get("identity_id"),
            item.get("notes"),
            ts,
        ),
    )
    return lid


def _upsert_hypothesis(
    conn: sqlite3.Connection, engagement_id: str, item: dict[str, Any]
) -> str:
    hid = str(item.get("id") or _new_id("H"))
    claim = str(item.get("claim") or "").strip()
    if not claim:
        raise WarboardError(f"hypothesis {hid}: claim required")
    status = str(item.get("status") or "open")
    ts = now_iso()
    notes = item.get("notes")
    probe = item.get("probe")
    if probe:
        notes = f"probe:{probe}" if not notes else f"{notes}\nprobe:{probe}"
    row = conn.execute("SELECT id FROM hypotheses WHERE id=?", (hid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE hypotheses SET claim=?, status=?, expect=?, kill_if=?, notes=?, "
            "updated_at=? WHERE id=?",
            (
                claim,
                status,
                item.get("expect"),
                item.get("kill_if"),
                notes,
                ts,
                hid,
            ),
        )
        return hid
    conn.execute(
        "INSERT INTO hypotheses(id, engagement_id, claim, status, related_asset_id, "
        "related_surface_id, expect, kill_if, notes, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            hid,
            engagement_id,
            claim,
            status,
            item.get("related_asset_id"),
            item.get("related_surface_id"),
            item.get("expect"),
            item.get("kill_if"),
            notes,
            ts,
            ts,
        ),
    )
    return hid


def _upsert_goal(
    conn: sqlite3.Connection, engagement_id: str, item: dict[str, Any]
) -> str:
    gid = str(item.get("id") or _new_id("G"))
    title = str(item.get("title") or "").strip()
    if not title:
        raise WarboardError(f"goal {gid}: title required")
    status = str(item.get("status") or "active")
    ts = now_iso()
    row = conn.execute("SELECT id FROM goals WHERE id=?", (gid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE goals SET title=?, status=?, success_criteria=?, notes=?, "
            "updated_at=? WHERE id=?",
            (
                title,
                status,
                item.get("success_criteria"),
                item.get("notes"),
                ts,
                gid,
            ),
        )
        return gid
    conn.execute(
        "INSERT INTO goals(id, engagement_id, title, status, success_criteria, notes, "
        "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            gid,
            engagement_id,
            title,
            status,
            item.get("success_criteria"),
            item.get("notes"),
            ts,
            ts,
        ),
    )
    return gid


def _upsert_identity(
    conn: sqlite3.Connection, engagement_id: str, realm_id: str, item: dict[str, Any]
) -> str:
    iid = str(item.get("id") or _new_id("I"))
    label = str(item.get("label") or "").strip()
    if not label:
        raise WarboardError(f"identity {iid}: label required")
    kind = str(item.get("kind") or "other")
    band = str(item.get("privilege_band") or "unknown")
    ts = now_iso()
    row = conn.execute("SELECT id FROM identities WHERE id=?", (iid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE identities SET label=?, kind=?, privilege_band=?, notes=? WHERE id=?",
            (label, kind, band, item.get("notes"), iid),
        )
        return iid
    conn.execute(
        "INSERT INTO identities(id, engagement_id, realm_id, label, kind, "
        "privilege_band, asset_id, notes, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            iid,
            engagement_id,
            realm_id,
            label,
            kind,
            band,
            item.get("asset_id"),
            item.get("notes"),
            ts,
        ),
    )
    return iid


def apply_facts(conn: sqlite3.Connection, facts: dict[str, Any], *, fresh: bool = False) -> str:
    if not isinstance(facts, dict):
        raise WarboardError("facts must be an object")
    eng = facts.get("engagement") if isinstance(facts.get("engagement"), dict) else {}
    eid = ensure_engagement(
        conn,
        fresh=fresh,
        name=str(eng.get("name") or "engagement"),
        mode=str(eng.get("mode") or "ctf"),
        scope_notes=eng.get("scope_notes"),
    )
    realm_id = default_realm_id(conn, eid)
    if eng.get("scope_notes") or eng.get("name"):
        conn.execute(
            "UPDATE engagements SET name=?, scope_notes=?, updated_at=? WHERE id=?",
            (
                str(eng.get("name") or "engagement"),
                eng.get("scope_notes"),
                now_iso(),
                eid,
            ),
        )
    for item in facts.get("assets") or []:
        if not isinstance(item, dict):
            raise WarboardError("assets[] must be objects")
        _upsert_asset(conn, eid, realm_id, item)
    for item in facts.get("surfaces") or []:
        if not isinstance(item, dict):
            raise WarboardError("surfaces[] must be objects")
        _upsert_surface(conn, eid, item)
    for item in facts.get("identities") or []:
        if not isinstance(item, dict):
            raise WarboardError("identities[] must be objects")
        _upsert_identity(conn, eid, realm_id, item)
    for item in facts.get("loot") or []:
        if not isinstance(item, dict):
            raise WarboardError("loot[] must be objects")
        _insert_loot(conn, eid, item)
    for item in facts.get("hypotheses") or []:
        if not isinstance(item, dict):
            raise WarboardError("hypotheses[] must be objects")
        _upsert_hypothesis(conn, eid, item)
    for item in facts.get("goals") or []:
        if not isinstance(item, dict):
            raise WarboardError("goals[] must be objects")
        _upsert_goal(conn, eid, item)
    campaign = load_campaign(conn, eid)
    incoming = facts.get("campaign")
    if isinstance(incoming, dict):
        merged = _parse_campaign(json.dumps({"campaign": incoming}))
        campaign.update({k: v for k, v in merged.items() if k != "campaign_surfaces"})
        if incoming.get("campaign_surfaces"):
            campaign["campaign_surfaces"].update(incoming["campaign_surfaces"])
        save_campaign(conn, eid, campaign)
    focus = facts.get("focus") if isinstance(facts.get("focus"), dict) else None
    if focus:
        ts = now_iso()
        row = conn.execute(
            "SELECT id FROM focus WHERE engagement_id=?", (eid,)
        ).fetchone()
        phase = str(focus.get("phase") or "map")
        summary = focus.get("summary")
        active_asset = focus.get("active_asset_id")
        active_goal = focus.get("active_goal_id")
        if row:
            conn.execute(
                "UPDATE focus SET phase=?, summary=?, active_asset_id=?, "
                "active_goal_id=?, updated_at=? WHERE engagement_id=?",
                (phase, summary, active_asset, active_goal, ts, eid),
            )
        else:
            conn.execute(
                "INSERT INTO focus(id, engagement_id, phase, summary, active_asset_id, "
                "active_goal_id, pending_decision_json, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    _new_id("F"),
                    eid,
                    phase,
                    summary,
                    active_asset,
                    active_goal,
                    _dump_pending(campaign),
                    ts,
                ),
            )
    conn.execute(
        "INSERT INTO events(id, engagement_id, kind, body_json, actor, "
        "related_focus_id, created_at) VALUES (?, ?, 'state_change', ?, 'agent', NULL, ?)",
        (
            _new_id("EV"),
            eid,
            json.dumps({"op": "apply", "keys": sorted(facts.keys())}, ensure_ascii=False),
            now_iso(),
        ),
    )
    conn.execute(
        "UPDATE engagements SET updated_at=? WHERE id=?",
        (now_iso(), eid),
    )
    conn.commit()
    return eid


def render_brief(
    conn: sqlite3.Connection,
    engagement_id: str,
    *,
    state_root: Path,
    full: bool = False,
) -> str:
    eng = conn.execute(
        "SELECT * FROM engagements WHERE id=?", (engagement_id,)
    ).fetchone()
    campaign = load_campaign(conn, engagement_id)
    n_assets = conn.execute(
        "SELECT COUNT(*) AS n FROM assets WHERE engagement_id=?", (engagement_id,)
    ).fetchone()["n"]
    n_surfaces = conn.execute(
        "SELECT COUNT(*) AS n FROM surfaces WHERE engagement_id=?", (engagement_id,)
    ).fetchone()["n"]
    observed = observed_surface_count(conn, engagement_id)
    open_h = open_hypothesis_count(conn, engagement_id)
    n_loot = conn.execute(
        "SELECT COUNT(*) AS n FROM loot WHERE engagement_id=?", (engagement_id,)
    ).fetchone()["n"]
    rnd = current_round(conn, engagement_id)
    lines = [
        (
            f"WARBOARD status={eng['status']} engagement={engagement_id} "
            f"round={rnd} mode={eng['mode']}"
        ),
        f"scope={eng['scope_notes'] or ''}",
        f"HAVE={campaign.get('have') or ''}",
        f"Goal={campaign.get('goal') or ''}",
        f"next_probe={campaign.get('next_probe') or ''}",
        f"materials={campaign.get('materials')}",
        f"assets={n_assets} surfaces={n_surfaces} observed={observed} "
        f"hypotheses_open={open_h} loot={n_loot}",
    ]
    gaps: list[str] = []
    if not str(campaign.get("have", "")).strip():
        gaps.append("have")
    if campaign.get("materials") == "unread":
        gaps.append("materials")
    camp_sur = campaign.get("campaign_surfaces") or {}
    for name in hunt_plan.SURFACE_CLASSES:
        if str(camp_sur.get(name, "untested")) not in CAMPAIGN_OK:
            gaps.append(f"surface.{name}")
    if observed == 0 and str(camp_sur.get("transport", "untested")) not in CAMPAIGN_OK:
        gaps.append("no_surface")
    if open_h == 0:
        gaps.append("bet")
    if not str(campaign.get("goal", "")).strip():
        gaps.append("goal")
    if not str(campaign.get("next_probe", "")).strip():
        gaps.append("next_probe")
    lines.append("gaps=" + (",".join(gaps) if gaps else "none"))
    for row in conn.execute(
        "SELECT id, claim, status, expect, kill_if FROM hypotheses "
        "WHERE engagement_id=? AND status='open' ORDER BY id",
        (engagement_id,),
    ):
        lines.append(
            f"bet {row['id']} status={row['status']} claim={row['claim']} "
            f"expect={row['expect'] or ''} kill_if={row['kill_if'] or ''}"
        )
    for row in conn.execute(
        "SELECT id, kind, sensitivity, label, storage_ref FROM loot "
        "WHERE engagement_id=? ORDER BY created_at",
        (engagement_id,),
    ):
        lines.append(
            f"loot {row['id']} kind={row['kind']} sensitivity={row['sensitivity']} "
            f"label={row['label']} ref={row['storage_ref'] or ''}"
        )
    debt = markdown_debt_names(state_root)
    if debt:
        lines.append("WARNING markdown_debt=" + ",".join(debt) + " unused")
    if full:
        lines.append("campaign=" + json.dumps(campaign, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def cmd_opening(
    text: str,
    *,
    state_root: Path,
    db: Path,
    ports_known: bool,
    observe_complete: bool,
    fresh: bool,
) -> int:
    conn = connect(db, create=True)
    try:
        eid = ensure_engagement(conn, fresh=fresh)
        start_round(conn, eid)
        conn.commit()
        intent = hunt_plan.opening_intent(
            text,
            ports_known=ports_known,
            observe_complete_flag=observe_complete,
        )
        print(intent)
        print(hunt_plan.format_loaded_line())
        sys.stdout.write(render_brief(conn, eid, state_root=state_root))
        return 0
    finally:
        conn.close()


def cmd_brief(state_root: Path, db: Path, full: bool) -> int:
    conn = connect(db, create=False)
    try:
        eng = active_engagement(conn)
        if eng is None:
            print("WARBOARD status=empty", file=sys.stderr)
            return 1
        sys.stdout.write(
            render_brief(conn, str(eng["id"]), state_root=state_root, full=full)
        )
        return 0
    finally:
        conn.close()


def cmd_apply(facts_path: str, state_root: Path, db: Path, fresh: bool) -> int:
    if facts_path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(facts_path).read_text(encoding="utf-8")
    try:
        facts = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid facts JSON: {exc}", file=sys.stderr)
        return 1
    conn = connect(db, create=True)
    try:
        eid = apply_facts(conn, facts, fresh=fresh)
        sys.stdout.write(render_brief(conn, eid, state_root=state_root))
        return 0
    except WarboardError as exc:
        print(f"ERROR: facts rejected; sqlite not changed\n{exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Warboard SQLite engagement runtime")
    parser.add_argument(
        "--state-root",
        type=Path,
        default=DEFAULT_STATE_ROOT,
        help="engagement directory (default: ./pentest-state)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="sqlite path (default: <state-root>/warboard.sqlite)",
    )
    parser.add_argument(
        "--print-schema",
        action="store_true",
        help="print apply --facts JSON shape and exit",
    )
    sub = parser.add_subparsers(dest="cmd")

    opening = sub.add_parser("opening", help="ensure db, start a round, print brief")
    opening.add_argument("text")
    opening.add_argument("--ports-known", action="store_true")
    opening.add_argument("--observe-complete", action="store_true")
    opening.add_argument(
        "--fresh",
        action="store_true",
        help="pause the active engagement and start a new one",
    )

    brief = sub.add_parser("brief", help="print sqlite stance; never dump markdown")
    brief.add_argument("--full", action="store_true")

    apply_p = sub.add_parser("apply", help="upsert facts JSON into sqlite")
    apply_p.add_argument("--facts", required=True, help="facts JSON path, or - for stdin")
    apply_p.add_argument("--fresh", action="store_true")

    args = parser.parse_args(argv)
    if args.print_schema:
        print(json.dumps(FACTS_SCHEMA, ensure_ascii=False, indent=2))
        return 0
    if not args.cmd:
        parser.print_help()
        return 2
    state_root = args.state_root
    db = args.db if args.db is not None else db_path_for(state_root)
    try:
        if args.cmd == "opening":
            return cmd_opening(
                args.text,
                state_root=state_root,
                db=db,
                ports_known=args.ports_known,
                observe_complete=args.observe_complete,
                fresh=args.fresh,
            )
        if args.cmd == "brief":
            return cmd_brief(state_root, db, args.full)
        if args.cmd == "apply":
            return cmd_apply(args.facts, state_root, db, args.fresh)
    except WarboardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
