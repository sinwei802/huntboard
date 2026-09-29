#!/usr/bin/env python3
"""Local warboard page: read the board, switch the active engagement, hide secrets."""

from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import warboard  # noqa: E402
import warboard_console as console  # noqa: E402


def _seed(root: Path) -> tuple[Path, str, str]:
    db = root / "warboard.sqlite"
    conn = warboard.connect(db, create=True)
    try:
        first = warboard.apply_facts(
            conn,
            {
                "engagement": {"name": "first", "mode": "ctf", "scope_notes": "10.10.11.1"},
                "assets": [{"id": "A-old", "address": "10.10.11.1", "status": "reachable"}],
            },
        )
        second = warboard.apply_facts(
            conn,
            {
                "engagement": {"name": "lab", "mode": "ctf", "scope_notes": "10.10.11.2"},
                "assets": [{"id": "A-web", "hostname": "web", "address": "10.10.11.2", "status": "mapped"}],
                "surfaces": [
                    {
                        "id": "S-1",
                        "asset_id": "A-web",
                        "kind": "http",
                        "port": 80,
                        "status": "seen",
                        "banner_or_product": "nginx",
                    }
                ],
                "hypotheses": [
                    {
                        "id": "H-1",
                        "claim": "未認證目錄",
                        "status": "open",
                        "expect": "namingContexts",
                        "kill_if": "不可達",
                    }
                ],
                "goals": [{"id": "G-1", "title": "取得具名身份", "status": "active"}],
                "identities": [{"id": "I-1", "label": "anonymous", "kind": "anonymous"}],
                "loot": [
                    {
                        "id": "L-secret",
                        "kind": "hash",
                        "sensitivity": "high",
                        "label": "asrep",
                        "storage_ref": "loot/asrep.hash",
                        "notes": "SECRET-NOTE-should-stay-in-db",
                    },
                    {
                        "id": "L-file",
                        "kind": "file",
                        "sensitivity": "low",
                        "label": "readme",
                        "storage_ref": "loot/readme.txt",
                        "notes": "plain note",
                    },
                ],
                "campaign": {
                    "have": "anonymous http",
                    "materials": "none",
                    "next_probe": "LDAP rootDSE",
                    "goal": "取得具名身份",
                    "campaign_surfaces": {
                        "transport": "seen",
                        "identity_unauth": "seen",
                        "naming": "seen",
                        "materials": "seen",
                    },
                },
                "focus": {
                    "phase": "map",
                    "summary": "看 80",
                    "active_asset_id": "A-web",
                    "active_goal_id": "G-1",
                },
            },
            fresh=True,
        )
        warboard.start_round(conn, second)
        warboard.start_round(conn, second)
        conn.execute(
            "INSERT INTO events(id, engagement_id, kind, body_json, actor, "
            "related_focus_id, created_at) VALUES (?, ?, 'note', ?, 'agent', NULL, ?)",
            (
                "EV-secret",
                second,
                json.dumps({"op": "seen", "password": "p@ss-should-not-leak"}),
                warboard.now_iso(),
            ),
        )
        conn.commit()
        return db, first, second
    finally:
        conn.close()


class ConsoleSnapshotTest(unittest.TestCase):
    def test_board_matches_brief_and_hides_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db, _first, second = _seed(root)
            board = console.snapshot(db, root, second)
            self.assertFalse(board["empty"])
            self.assertEqual(board["engagement"]["name"], "lab")
            self.assertEqual(board["rows"][0]["host"], "web")
            self.assertEqual(board["rows"][0]["port"], 80)
            self.assertEqual(board["focus"]["active_goal"], "取得具名身份")
            self.assertEqual(board["hypotheses"][0]["expect"], "namingContexts")
            conn = warboard.connect(db, create=False)
            try:
                brief = warboard.render_brief(conn, second, state_root=root)
            finally:
                conn.close()
            gap_line = next(line for line in brief.splitlines() if line.startswith("gaps="))
            expected = [] if gap_line == "gaps=none" else gap_line.split("=", 1)[1].split(",")
            self.assertEqual(board["gaps"], expected)
            raw = json.dumps(board, ensure_ascii=False)
            self.assertNotIn("SECRET-NOTE-should-stay-in-db", raw)
            self.assertNotIn("p@ss-should-not-leak", raw)
            self.assertIn("〔已隱藏〕", raw)
            secret = next(item for item in board["loot"] if item["id"] == "L-secret")
            self.assertNotIn("notes", secret)
            self.assertEqual(secret["storage_ref"], "loot/asrep.hash")
            plain = next(item for item in board["loot"] if item["id"] == "L-file")
            self.assertEqual(plain["notes"], "plain note")
            self.assertGreaterEqual(len(board["rounds"]), 2)
            self.assertTrue(board["rounds"][-1]["open"])
            self.assertFalse(board["rounds"][0]["open"])
            self.assertEqual(board["rounds"][-1]["n"], 2)

    def test_activate_pauses_the_other_and_only_inserts_an_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db, first, second = _seed(root)
            conn = warboard.connect(db, create=False)
            try:
                before = [row["id"] for row in conn.execute("SELECT id FROM events ORDER BY id")]
            finally:
                conn.close()
            console.set_active(db, first)
            conn = warboard.connect(db, create=False)
            try:
                active = warboard.active_engagement(conn)
                self.assertEqual(active["id"], first)
                other = conn.execute(
                    "SELECT status FROM engagements WHERE id=?", (second,)
                ).fetchone()
                self.assertEqual(other["status"], "paused")
                after = [row["id"] for row in conn.execute("SELECT id FROM events ORDER BY id")]
            finally:
                conn.close()
            self.assertTrue(set(before).issubset(after))
            self.assertEqual(len(after), len(before) + 1)

    def test_missing_db_does_not_create_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "missing.sqlite"
            board = console.snapshot(db, Path(tmp))
            self.assertTrue(board["empty"])
            self.assertEqual(board["reason"], "db_missing")
            self.assertFalse(db.exists())


class ConsoleHttpTest(unittest.TestCase):
    def test_page_and_post_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db, first, second = _seed(root)
            server = console.make_server(db, root, "127.0.0.1", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            host, port = server.server_address[:2]
            base = f"http://{host}:{port}"
            try:
                page = urllib.request.urlopen(base + "/", timeout=5)
                html = page.read().decode("utf-8")
                self.assertIn("HuntSpear 作戰台", html)
                self.assertIn("/api/board", html)
                board = json.load(
                    urllib.request.urlopen(
                        base + "/api/board?engagement=" + second, timeout=5
                    )
                )
                self.assertEqual(board["engagement"]["id"], second)
                self.assertNotIn("p@ss-should-not-leak", json.dumps(board))
                evil = urllib.request.Request(
                    base + "/api/engagements/" + first + "/activate",
                    data=b"{}",
                    method="POST",
                    headers={"Origin": "http://evil.example", "Content-Type": "application/json"},
                )
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(evil, timeout=5)
                self.assertEqual(caught.exception.code, 403)
                caught.exception.close()
                rename = urllib.request.Request(
                    base + "/api/engagements/" + second,
                    data=json.dumps({"name": "lab-renamed", "scope_notes": "10.10.11.9"}).encode(),
                    method="POST",
                    headers={
                        "Origin": f"http://{host}:{port}",
                        "Content-Type": "application/json",
                    },
                )
                self.assertEqual(urllib.request.urlopen(rename, timeout=5).status, 200)
                renamed = json.load(
                    urllib.request.urlopen(
                        base + "/api/board?engagement=" + second, timeout=5
                    )
                )
                self.assertEqual(renamed["engagement"]["name"], "lab-renamed")
                self.assertEqual(renamed["engagement"]["scope_notes"], "10.10.11.9")
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
