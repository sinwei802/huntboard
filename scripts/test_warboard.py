#!/usr/bin/env python3
"""Warboard sqlite is the engagement truth. Markdown core files are unused debt."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WB = ROOT / "warboard.py"
GATE = ROOT / "sense_gate.py"
SKILL = ROOT.parent / "SKILL.md"


def _run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class WarboardRuntimeTest(unittest.TestCase):
    def test_opening_creates_sqlite_and_ignores_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "asset-graph.md").write_text("# Asset Graph\nHAVE should not load\n")
            (root / "hunt-plan.md").write_text("goal: 不該當本期前提\n")
            proc = _run(
                [str(WB), "--state-root", str(root), "opening", "開局掃 10.10.11.1"]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            lines = proc.stdout.splitlines()
            self.assertEqual(lines[0], "observe_transport")
            self.assertTrue(lines[1].startswith("loaded="), proc.stdout)
            self.assertIn("WARBOARD status=active", proc.stdout)
            self.assertIn("markdown_debt=asset-graph.md,hunt-plan.md unused", proc.stdout)
            self.assertNotIn("HAVE should not load", proc.stdout)
            self.assertNotIn("不該當本期前提", proc.stdout)
            self.assertTrue((root / "warboard.sqlite").is_file())

    def test_apply_then_brief_does_not_write_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            facts = {
                "engagement": {"name": "lab", "mode": "ctf", "scope_notes": "10.10.11.1"},
                "assets": [{"id": "A-1", "address": "10.10.11.1", "status": "reachable"}],
                "surfaces": [
                    {
                        "id": "S-1",
                        "asset_id": "A-1",
                        "kind": "tcp",
                        "port": 80,
                        "status": "seen",
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
            }
            facts_path = root / "facts.json"
            facts_path.write_text(json.dumps(facts), encoding="utf-8")
            apply = _run(
                [str(WB), "--state-root", str(root), "apply", "--facts", str(facts_path)]
            )
            self.assertEqual(apply.returncode, 0, apply.stderr)
            self.assertIn("HAVE=anonymous http", apply.stdout)
            self.assertIn("bet H-1", apply.stdout)
            self.assertIn("gaps=none", apply.stdout)
            for name in (
                "asset-graph.md",
                "route-stack.md",
                "loot-tracker.md",
                "session-index.json",
                "evidence-index.json",
                "hunt-plan.md",
            ):
                self.assertFalse((root / name).exists(), name)
            brief = _run([str(WB), "--state-root", str(root), "brief"])
            self.assertEqual(brief.returncode, 0, brief.stderr)
            self.assertIn("Goal=取得具名身份", brief.stdout)

    def test_observe_passes_empty_board_exploit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            opening = _run(
                [str(WB), "--state-root", str(root), "opening", "開局掃 10.10.11.1"]
            )
            self.assertEqual(opening.returncode, 0, opening.stderr)
            db = root / "warboard.sqlite"
            observe = _run([str(GATE), "--db", str(db), "--action", "observe"])
            self.assertEqual(observe.returncode, 0, observe.stderr)
            exploit = _run([str(GATE), "--db", str(db), "--action", "exploit"])
            self.assertEqual(exploit.returncode, 1)
            self.assertIn("h1_no_surface", exploit.stderr)
            self.assertIn("h2_no_bet", exploit.stderr)

    def test_db_gate_ignores_proposal_self_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _run([str(WB), "--state-root", str(root), "opening", "開局掃 10.10.11.1"])
            proposal = {
                "phase": "probe",
                "hypothesis": "我說觀察已經齊了所以可以打",
                "evidence_gate": "已觀測完整 GET 往返含狀態碼與至少兩標頭",
                "dead_if": "連續兩次僅空回應 → DEAD:http-thin",
                "card_id": "http-observe-only",
                "cloud_cross": ["src-rfc-mdn", "src-websearch"],
                "action_class": "exploit",
            }
            path = root / "proposal.json"
            path.write_text(json.dumps(proposal), encoding="utf-8")
            proc = _run(
                [
                    str(GATE),
                    "--db",
                    str(root / "warboard.sqlite"),
                    "--action",
                    "exploit",
                    "--check",
                    str(path),
                ]
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("h1_no_have", proc.stderr)
            self.assertIn("h2_no_bet", proc.stderr)

    def test_r2_blocks_same_round_secret(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _run([str(WB), "--state-root", str(root), "opening", "開局掃 10.10.11.1"])
            facts = {
                "assets": [{"id": "A-1", "address": "10.10.11.1", "status": "reachable"}],
                "surfaces": [
                    {
                        "id": "S-1",
                        "asset_id": "A-1",
                        "kind": "tcp",
                        "port": 88,
                        "status": "seen",
                    }
                ],
                "hypotheses": [
                    {
                        "id": "H-1",
                        "claim": "AS-REP 可離線",
                        "status": "open",
                        "expect": "hash",
                        "kill_if": "不可預認證",
                    }
                ],
                "goals": [{"id": "G-1", "title": "取得具名身份", "status": "active"}],
                "loot": [
                    {
                        "id": "L-1",
                        "kind": "hash",
                        "sensitivity": "high",
                        "label": "asrep-svc",
                        "storage_ref": "loot/svc.asrep",
                    }
                ],
                "campaign": {
                    "have": "asrep hash",
                    "materials": "unread",
                    "next_probe": "auth_use",
                    "goal": "取得具名身份",
                    "campaign_surfaces": {
                        "transport": "seen",
                        "identity_unauth": "seen",
                        "naming": "seen",
                        "materials": "seen",
                    },
                },
            }
            facts_path = root / "facts.json"
            facts_path.write_text(json.dumps(facts), encoding="utf-8")
            apply = _run(
                [str(WB), "--state-root", str(root), "apply", "--facts", str(facts_path)]
            )
            self.assertEqual(apply.returncode, 0, apply.stderr)
            db = root / "warboard.sqlite"
            # materials unread still blocks H1; set read via second apply then R2.
            facts["campaign"]["materials"] = "read"
            facts_path.write_text(json.dumps(facts), encoding="utf-8")
            _run([str(WB), "--state-root", str(root), "apply", "--facts", str(facts_path)])
            auth = _run([str(GATE), "--db", str(db), "--action", "auth_use"])
            self.assertEqual(auth.returncode, 1, auth.stderr)
            self.assertIn("r2_same_round_secret", auth.stderr)
            _run([str(WB), "--state-root", str(root), "opening", "繼續"])
            later = _run([str(GATE), "--db", str(db), "--action", "auth_use"])
            self.assertEqual(later.returncode, 0, later.stderr)

    def test_print_schema(self) -> None:
        proc = _run([str(WB), "--print-schema"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("campaign", data)
        self.assertIn("assets", data)

    def test_skill_wires_sqlite_not_markdown_bundle(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("warboard.py", text)
        self.assertIn("warboard.sqlite", text)
        self.assertIn("**R6｜", text)
        self.assertIn("sense_gate.py --db", text)
        self.assertIn("禁止把 markdown bundle", text)
        self.assertNotIn("load_state_bundle.py", text)
        self.assertNotIn("checkpoint_write.py", text)


if __name__ == "__main__":
    unittest.main()
