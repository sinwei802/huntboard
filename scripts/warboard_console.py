#!/usr/bin/env python3
"""Local warboard page. Reads sqlite; does not grant actions.

Default listen address is 127.0.0.1:8765. Combat rows stay on
``warboard.py apply``. This page can switch which engagement is active
and edit its name and scope. Events are insert-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import hunt_plan  # noqa: E402
import warboard  # noqa: E402

HTML_PATH = _SCRIPTS.parent / "console" / "board.html"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SECRET_KEY = re.compile(
    r"password|passwd|secret|token|cookie|hash|credential|ntlm",
    re.IGNORECASE,
)
MAX_BODY = 65536


def redact(value: Any, depth: int = 0) -> Any:
    if depth > 6:
        return "…"
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if _SECRET_KEY.search(str(key)):
                out[str(key)] = "〔已隱藏〕"
            else:
                out[str(key)] = redact(item, depth + 1)
        return out
    if isinstance(value, list):
        return [redact(item, depth + 1) for item in value[:30]]
    if isinstance(value, str) and len(value) > 240:
        return value[:240] + "…"
    return value


def stance_gaps(
    conn: sqlite3.Connection, engagement_id: str, campaign: dict[str, Any]
) -> list[str]:
    """Same gap names as ``warboard.render_brief``."""
    observed = warboard.observed_surface_count(conn, engagement_id)
    open_h = warboard.open_hypothesis_count(conn, engagement_id)
    gaps: list[str] = []
    if not str(campaign.get("have", "")).strip():
        gaps.append("have")
    if campaign.get("materials") == "unread":
        gaps.append("materials")
    surfaces = campaign.get("campaign_surfaces") or {}
    for name in hunt_plan.SURFACE_CLASSES:
        if str(surfaces.get(name, "untested")) not in warboard.CAMPAIGN_OK:
            gaps.append(f"surface.{name}")
    if observed == 0 and str(surfaces.get("transport", "untested")) not in warboard.CAMPAIGN_OK:
        gaps.append("no_surface")
    if open_h == 0:
        gaps.append("bet")
    if not str(campaign.get("goal", "")).strip():
        gaps.append("goal")
    if not str(campaign.get("next_probe", "")).strip():
        gaps.append("next_probe")
    return gaps


def _split_pending(raw: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    campaign = warboard._parse_campaign(raw)
    pending: dict[str, Any] = {
        "options": [],
        "selected_option_id": None,
        "commander_utterance": None,
        "decided_at": None,
    }
    if not raw:
        return campaign, pending
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return campaign, pending
    if not isinstance(parsed, dict):
        return campaign, pending
    if isinstance(parsed.get("options"), list):
        pending["options"] = redact(parsed.get("options"))
        pending["selected_option_id"] = parsed.get("selected_option_id")
        pending["commander_utterance"] = redact(parsed.get("commander_utterance"))
        pending["decided_at"] = parsed.get("decided_at")
    return campaign, pending


def _event_view(row: sqlite3.Row) -> dict[str, Any]:
    try:
        body = json.loads(row["body_json"])
    except json.JSONDecodeError:
        body = {"raw": str(row["body_json"])[:240]}
    return {
        "id": row["id"],
        "kind": row["kind"],
        "actor": row["actor"],
        "created_at": row["created_at"],
        "body": redact(body),
    }


def fold_events(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    rounds: list[dict[str, Any]] = []
    current: dict[str, Any] = {"n": 0, "events": []}
    for row in rows:
        view = _event_view(row)
        body = view["body"] if isinstance(view["body"], dict) else {}
        if view["kind"] == "note" and body.get("op") == "round_start":
            if current["events"]:
                rounds.append(current)
            try:
                number = int(body.get("n") or 0)
            except (TypeError, ValueError):
                number = 0
            current = {"n": number, "events": [view]}
        else:
            current["events"].append(view)
    if current["events"] or not rounds:
        rounds.append(current)
    last = len(rounds) - 1
    for index, item in enumerate(rounds):
        item["open"] = index == last
    return rounds


def _label(row: sqlite3.Row | None) -> str | None:
    if row is None:
        return None
    host = row["hostname"] or row["address"]
    return str(host) if host else None


def snapshot(
    db: Path, state_root: Path, engagement_id: str | None = None
) -> dict[str, Any]:
    db = db.expanduser()
    if not db.is_file():
        return {
            "empty": True,
            "reason": "db_missing",
            "db": str(db),
            "engagements": [],
            "selected_id": None,
        }
    conn = warboard.connect(db, create=False)
    try:
        engagements = [
            {
                "id": row["id"],
                "name": row["name"],
                "status": row["status"],
                "mode": row["mode"],
                "scope_notes": row["scope_notes"] or "",
                "updated_at": row["updated_at"],
            }
            for row in conn.execute(
                "SELECT id, name, status, mode, scope_notes, updated_at "
                "FROM engagements ORDER BY updated_at DESC"
            )
        ]
        if not engagements:
            return {
                "empty": True,
                "reason": "no_engagement",
                "db": str(db),
                "engagements": [],
                "selected_id": None,
                "markdown_debt": warboard.markdown_debt_names(state_root),
            }
        selected = engagement_id
        if selected is None or not any(item["id"] == selected for item in engagements):
            current = warboard.active_engagement(conn)
            selected = str(current["id"]) if current else engagements[0]["id"]
        eng = conn.execute(
            "SELECT * FROM engagements WHERE id=?", (selected,)
        ).fetchone()
        focus_row = conn.execute(
            "SELECT phase, summary, active_asset_id, active_goal_id, "
            "pending_decision_json FROM focus WHERE engagement_id=?",
            (selected,),
        ).fetchone()
        campaign, pending = _split_pending(
            focus_row["pending_decision_json"] if focus_row else None
        )
        asset_host = None
        goal_title = None
        if focus_row and focus_row["active_asset_id"]:
            asset_host = _label(
                conn.execute(
                    "SELECT hostname, address FROM assets WHERE id=?",
                    (focus_row["active_asset_id"],),
                ).fetchone()
            )
        if focus_row and focus_row["active_goal_id"]:
            goal = conn.execute(
                "SELECT title FROM goals WHERE id=?",
                (focus_row["active_goal_id"],),
            ).fetchone()
            goal_title = str(goal["title"]) if goal else None
        rows = [
            {
                "realm_id": row["realm_id"],
                "realm": row["realm"],
                "asset_id": row["asset_id"],
                "host": row["host"],
                "asset_status": row["asset_status"],
                "surface_id": row["surface_id"],
                "surface_kind": row["surface_kind"],
                "port": row["port"],
                "path_or_name": row["path_or_name"],
                "banner_or_product": row["banner_or_product"],
                "surface_status": row["surface_status"],
            }
            for row in conn.execute(
                """
                SELECT
                  r.id AS realm_id,
                  r.name AS realm,
                  a.id AS asset_id,
                  COALESCE(a.hostname, a.address) AS host,
                  a.status AS asset_status,
                  s.id AS surface_id,
                  s.kind AS surface_kind,
                  s.port AS port,
                  s.path_or_name AS path_or_name,
                  s.banner_or_product AS banner_or_product,
                  s.status AS surface_status
                FROM assets a
                JOIN realms r ON r.id = a.realm_id
                LEFT JOIN surfaces s ON s.asset_id = a.id
                WHERE a.engagement_id = ?
                ORDER BY r.name, host, s.port, s.kind
                """,
                (selected,),
            )
        ]
        hypotheses = [
            {
                "id": row["id"],
                "claim": row["claim"],
                "status": row["status"],
                "expect": row["expect"] or "",
                "kill_if": row["kill_if"] or "",
            }
            for row in conn.execute(
                "SELECT id, claim, status, expect, kill_if FROM hypotheses "
                "WHERE engagement_id=? ORDER BY status, id",
                (selected,),
            )
        ]
        goals = [
            {
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
                "success_criteria": row["success_criteria"] or "",
            }
            for row in conn.execute(
                "SELECT id, title, status, success_criteria FROM goals "
                "WHERE engagement_id=? ORDER BY status, id",
                (selected,),
            )
        ]
        identities = [
            {
                "id": row["id"],
                "label": row["label"],
                "kind": row["kind"],
                "privilege_band": row["privilege_band"],
            }
            for row in conn.execute(
                "SELECT id, label, kind, privilege_band FROM identities "
                "WHERE engagement_id=? ORDER BY label",
                (selected,),
            )
        ]
        loot = []
        for row in conn.execute(
            "SELECT id, kind, sensitivity, label, storage_ref, notes FROM loot "
            "WHERE engagement_id=? ORDER BY created_at",
            (selected,),
        ):
            item = {
                "id": row["id"],
                "kind": row["kind"],
                "sensitivity": row["sensitivity"],
                "label": row["label"],
                "storage_ref": row["storage_ref"] or "",
            }
            if row["kind"] not in warboard.SENSITIVE_LOOT and row["notes"]:
                item["notes"] = redact(row["notes"])
            loot.append(item)
        events = fold_events(
            list(
                conn.execute(
                    "SELECT id, kind, body_json, actor, created_at FROM events "
                    "WHERE engagement_id=? ORDER BY created_at, id",
                    (selected,),
                )
            )
        )
        return {
            "empty": False,
            "db": str(db),
            "selected_id": selected,
            "round": warboard.current_round(conn, selected),
            "engagements": engagements,
            "engagement": {
                "id": eng["id"],
                "name": eng["name"],
                "status": eng["status"],
                "mode": eng["mode"],
                "scope_notes": eng["scope_notes"] or "",
            },
            "campaign": campaign,
            "gaps": stance_gaps(conn, selected, campaign),
            "focus": {
                "phase": focus_row["phase"] if focus_row else "",
                "summary": (focus_row["summary"] or "") if focus_row else "",
                "active_asset_id": focus_row["active_asset_id"] if focus_row else None,
                "active_asset": asset_host,
                "active_goal_id": focus_row["active_goal_id"] if focus_row else None,
                "active_goal": goal_title,
                **pending,
            },
            "rows": rows,
            "hypotheses": hypotheses,
            "goals": goals,
            "identities": identities,
            "loot": loot,
            "rounds": events,
            "markdown_debt": warboard.markdown_debt_names(state_root),
        }
    finally:
        conn.close()


def _write_conn(db: Path) -> sqlite3.Connection:
    if not db.is_file():
        raise warboard.WarboardError(f"db_missing:{db}")
    conn = sqlite3.connect(str(db), timeout=5, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _append_note(conn: sqlite3.Connection, engagement_id: str, body: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO events(id, engagement_id, kind, body_json, actor, "
        "related_focus_id, created_at) VALUES (?, ?, 'note', ?, 'commander', NULL, ?)",
        (
            warboard._new_id("EV"),
            engagement_id,
            json.dumps(body, ensure_ascii=False),
            warboard.now_iso(),
        ),
    )


def set_active(db: Path, engagement_id: str) -> None:
    if not _ID.fullmatch(engagement_id):
        raise warboard.WarboardError("bad_id")
    conn = _write_conn(db)
    started = False
    try:
        row = conn.execute(
            "SELECT id, status FROM engagements WHERE id=?", (engagement_id,)
        ).fetchone()
        if row is None:
            raise warboard.WarboardError(f"missing_engagement:{engagement_id}")
        others = conn.execute(
            "SELECT COUNT(*) AS n FROM engagements WHERE status='active' AND id!=?",
            (engagement_id,),
        ).fetchone()
        if row["status"] == "active" and int(others["n"]) == 0:
            return
        ts = warboard.now_iso()
        conn.execute("BEGIN IMMEDIATE")
        started = True
        conn.execute(
            "UPDATE engagements SET status='paused', updated_at=? "
            "WHERE status='active' AND id!=?",
            (ts, engagement_id),
        )
        conn.execute(
            "UPDATE engagements SET status='active', updated_at=? WHERE id=?",
            (ts, engagement_id),
        )
        _append_note(conn, engagement_id, {"op": "console_activate"})
        conn.execute("COMMIT")
    except Exception:
        if started:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def update_engagement(
    db: Path,
    engagement_id: str,
    *,
    name: str | None,
    scope_notes: str | None,
    touch_scope: bool,
) -> None:
    if not _ID.fullmatch(engagement_id):
        raise warboard.WarboardError("bad_id")
    if name is not None:
        if not isinstance(name, str):
            raise warboard.WarboardError("bad_name")
        name = name.strip()
        if not name or len(name) > 200:
            raise warboard.WarboardError("bad_name")
    if touch_scope:
        if scope_notes is None:
            scope_notes = ""
        if not isinstance(scope_notes, str) or len(scope_notes) > 4000:
            raise warboard.WarboardError("bad_scope")
    conn = _write_conn(db)
    started = False
    try:
        row = conn.execute(
            "SELECT name, scope_notes FROM engagements WHERE id=?",
            (engagement_id,),
        ).fetchone()
        if row is None:
            raise warboard.WarboardError(f"missing_engagement:{engagement_id}")
        next_name = name if name is not None else str(row["name"])
        next_scope = scope_notes if touch_scope else row["scope_notes"]
        ts = warboard.now_iso()
        conn.execute("BEGIN IMMEDIATE")
        started = True
        conn.execute(
            "UPDATE engagements SET name=?, scope_notes=?, updated_at=? WHERE id=?",
            (next_name, next_scope, ts, engagement_id),
        )
        _append_note(
            conn,
            engagement_id,
            {"op": "console_rename", "name": next_name},
        )
        conn.execute("COMMIT")
    except Exception:
        if started:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


class ConsoleHandler(BaseHTTPRequestHandler):
    db: Path
    state_root: Path
    html: bytes

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _origin_ok(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        host = self.headers.get("Host", "")
        return origin in {f"http://{host}", f"https://{host}"}

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        self._send(
            code,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise warboard.WarboardError("body_too_large")
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        parsed = json.loads(raw.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise warboard.WarboardError("body_must_be_object")
        return parsed

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(200, self.html, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/board":
            query = parse_qs(parsed.query)
            requested = (query.get("engagement") or [None])[0]
            if requested is not None and not _ID.fullmatch(requested):
                self._json(400, {"error": "bad_id"})
                return
            self._json(200, snapshot(self.db, self.state_root, requested))
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self._origin_ok():
            self._json(403, {"error": "bad_origin"})
            return
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        try:
            if (
                len(parts) == 4
                and parts[0] == "api"
                and parts[1] == "engagements"
                and parts[3] == "activate"
            ):
                set_active(self.db, parts[2])
                self._json(200, {"ok": True})
                return
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "engagements":
                payload = self._read_json()
                update_engagement(
                    self.db,
                    parts[2],
                    name=payload.get("name") if "name" in payload else None,
                    scope_notes=payload.get("scope_notes"),
                    touch_scope="scope_notes" in payload,
                )
                self._json(200, {"ok": True})
                return
        except warboard.WarboardError as exc:
            self._json(400, {"error": str(exc)})
            return
        except json.JSONDecodeError:
            self._json(400, {"error": "bad_json"})
            return
        self._json(404, {"error": "not_found"})


def make_server(db: Path, state_root: Path, host: str, port: int) -> ThreadingHTTPServer:
    if not HTML_PATH.is_file():
        raise warboard.WarboardError(f"missing_page:{HTML_PATH}")
    html = HTML_PATH.read_bytes()

    class Handler(ConsoleHandler):
        pass

    Handler.db = db
    Handler.state_root = state_root
    Handler.html = html
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local HuntSpear warboard page")
    parser.add_argument("--state-root", type=Path, default=warboard.DEFAULT_STATE_ROOT)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)
    db = args.db if args.db is not None else warboard.db_path_for(args.state_root)
    state_root = args.state_root
    try:
        server = make_server(db.expanduser(), state_root, args.host, args.port)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except warboard.WarboardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    host, port = server.server_address[:2]
    print(f"HuntSpear warboard  http://{host}:{port}/")
    print(f"db={db.expanduser()}")
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        print(f"listen={args.host} 這不是 loopback，同一網段看得到這頁。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
