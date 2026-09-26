#!/usr/bin/env python3
"""Drive checkpoint_write.py. One facts JSON must produce a valid bundle."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import checkpoint_write  # noqa: E402
import load_state_bundle  # noqa: E402


def _facts() -> dict:
    return {
        "mode": "ctf",
        "scope": ["10.0.0.1", "dc.example.vl"],
        "targets": [
            {
                "id": "A-0001",
                "ip": "10.0.0.1",
                "hostname": "dc.example.vl",
                "status": "active",
            }
        ],
        "assets": [
            {
                "id": "A-0001",
                "label": "DC",
                "kind": "host",
                "address": "10.0.0.1 / dc.example.vl",
                "state": "可達",
                "notes": "WS2022",
            }
        ],
        "routes": [
            {
                "id": "R-0001",
                "name": "Identity & Trust",
                "status": "active",
                "focus": "新身分剩餘觀察",
            }
        ],
        "hypotheses": [
            {
                "id": "H-0001",
                "priority": "HIGH",
                "claim": "新身分能讀 guest 讀不到的材料",
                "probe": "smb/ldap as user",
                "kill_if": "全 ACCESS_DENIED",
                "status": "active",
            }
        ],
        "closed": [
            {
                "id": "H-0002",
                "claim": "入職密碼對信裡兩帳有效",
                "status": "closed",
                "reopen_if": "發現別名",
            }
        ],
        "loot": [
            {
                "id": "L-0001",
                "kind": "password",
                "value": "example",
                "source": "Public pdf",
                "state": "已用",
                "use": "對 user 有效",
            }
        ],
        "evidence": [
            {
                "id": "E-0001",
                "state_refs": ["A-0001", "R-0001", "H-0001", "L-0001"],
                "claim": "10.0.0.1 是網域控制站",
                "relation": "supports",
                "confidence": "high",
                "freshness": "stable",
                "last_verified": "2026-09-21T12:00:00+08:00",
                "availability": "saved",
                "artifacts": [
                    {
                        "path": "loot/banner.txt",
                        "kind": "nxc",
                        "locator": "banner",
                    }
                ],
            }
        ],
        "last_stop": {
            "route": "R-0001",
            "hypothesis": "H-0001",
            "summary": "停在新身分剩餘觀察，尚未執行。",
        },
        "hunt_plan": {
            "phase": "OBSERVE",
            "goal": "用新身分看清網域",
            "have": "identity=example",
            "next_probe": "smb --shares",
            "attempts": 0,
            "untested": "該觀看者 shares",
            "adjust": "re-observe",
            "wildcard": "",
            "materials": "read",
            "last_expected": "真登入",
            "last_observed": "SMB [+]",
            "surfaces": {
                "transport": "seen",
                "identity_unauth": "seen",
                "naming": "seen",
                "materials": "seen",
            },
            "bets": [
                {
                    "id": "H-view",
                    "rank": 1,
                    "claim": "能讀目錄",
                    "probe": "ldap as user",
                    "expect": "物件列表",
                    "kill_if": "ACCESS_DENIED",
                    "status": "active",
                }
            ],
        },
    }


class CheckpointWriteTest(unittest.TestCase):
    def _prepare(self, base: Path) -> Path:
        root = base / "pentest-state"
        root.mkdir()
        loot = root / "loot"
        loot.mkdir()
        (loot / "banner.txt").write_text("DC banner\n", encoding="utf-8")
        return root

    def test_one_facts_file_writes_complete_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._prepare(Path(tmp))
            result = checkpoint_write.write_checkpoint(
                root, _facts(), checkpoint_id="cp-test"
            )
            self.assertEqual(result.status, 0, result.errors + result.warnings)
            self.assertIn("cp-test", result.loaded["session-index.json"])
            self.assertIn("| A-0001 |", result.loaded["asset-graph.md"])
            self.assertIn("1. **[H-0001] [HIGH]**", result.loaded["route-stack.md"])
            self.assertIn("| L-0001 |", result.loaded["loot-tracker.md"])
            self.assertIn("goal: 用新身分看清網域", result.loaded["hunt-plan.md"])
            loaded = json.loads(result.loaded["session-index.json"])
            self.assertEqual(loaded["last_stop"]["hypothesis"], "H-0001")

    def test_invalid_facts_leave_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._prepare(Path(tmp))
            good = checkpoint_write.write_checkpoint(
                root, _facts(), checkpoint_id="cp-keep"
            )
            self.assertEqual(good.status, 0, good.errors)
            before = (root / "session-index.json").read_text(encoding="utf-8")
            bad = dict(_facts())
            bad["targets"] = [
                {
                    "id": "A-9999",
                    "ip": "1.1.1.1",
                    "hostname": "nope",
                    "status": "active",
                }
            ]
            with self.assertRaises(checkpoint_write.CheckpointError):
                checkpoint_write.write_checkpoint(root, bad, checkpoint_id="cp-bad")
            after = (root / "session-index.json").read_text(encoding="utf-8")
            self.assertEqual(before, after)
            self.assertIn("cp-keep", after)

    def test_second_write_replaces_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._prepare(Path(tmp))
            checkpoint_write.write_checkpoint(root, _facts(), checkpoint_id="cp-1")
            updated = _facts()
            updated["assets"].append(
                {
                    "id": "A-0002",
                    "label": "apex",
                    "kind": "host",
                    "address": "192.168.1.22",
                    "state": "未測達",
                    "notes": "",
                }
            )
            updated["last_stop"]["summary"] = "補了內網 IP，仍未掃。"
            result = checkpoint_write.write_checkpoint(
                root, updated, checkpoint_id="cp-2"
            )
            self.assertEqual(result.status, 0, result.errors + result.warnings)
            self.assertIn("| A-0002 |", result.loaded["asset-graph.md"])
            self.assertIn("cp-2", result.loaded["session-index.json"])
            self.assertNotIn("cp-1", result.loaded["session-index.json"])

    def test_cli_print_schema_and_write(self) -> None:
        schema = subprocess.run(
            [sys.executable, str(SCRIPTS / "checkpoint_write.py"), "--print-schema"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(schema.returncode, 0, schema.stderr)
        self.assertIn('"mode": "ctf"', schema.stdout)
        self.assertIn('"assets"', schema.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = self._prepare(base)
            facts_path = base / "facts.json"
            facts_path.write_text(json.dumps(_facts()), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "checkpoint_write.py"),
                    "--facts",
                    str(facts_path),
                    "--id",
                    "cp-cli",
                    str(root),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("STATE_BUNDLE status=complete", proc.stdout)
            loaded = load_state_bundle.load_bundle(root)
            self.assertEqual(loaded.status, 0, loaded.errors + loaded.warnings)

    def test_cli_rejects_bad_json_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "empty-state"
            facts_path = Path(tmp) / "bad.json"
            facts_path.write_text("{", encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "checkpoint_write.py"),
                    "--facts",
                    str(facts_path),
                    str(root),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("not changed", proc.stderr)
            self.assertFalse((root / "session-index.json").exists())


if __name__ == "__main__":
    unittest.main()
