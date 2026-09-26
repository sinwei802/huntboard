#!/usr/bin/env python3
"""Tests for sense_gate — methodology fields only."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GATE = ROOT / "sense_gate.py"
SKILL = ROOT.parent / "SKILL.md"
LOCAL_SENSE = ROOT.parent / "references" / "local-sense.md"
CLOUD = ROOT.parent / "references" / "cloud-sources.md"
CARDS = ROOT.parent / "references" / "sense-cards"

CARD_FILES = (
    "http-observe-only.md",
    "evidence-gate.md",
    "dead-path-mark.md",
    "public-doc-cve-lookup.md",
    "local-sense-memory.md",
    "post-foothold-map.md",
    "priv-esc-evidence-gate.md",
    "web-app-evidence-ladder.md",
    "challenge-board-handoff.md",
    "session-break-rebuild.md",
)


def _run(payload: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
        name = f.name
    return subprocess.run(
        [sys.executable, str(GATE), "--check", name],
        capture_output=True,
        text=True,
    )


GOOD = {
    "phase": "probe",
    "hypothesis": "HTTP 面尚無認證邊界可標，需先完成往返指紋",
    "evidence_gate": "已觀測完整 GET 往返含狀態碼與至少兩標頭",
    "dead_if": "連續兩次僅空回應且無標頭 → DEAD:http-thin",
    "card_id": "http-observe-only",
    "cloud_cross": ["src-rfc-mdn", "src-websearch"],
    "action_class": "observe",
}


class SenseGateTests(unittest.TestCase):
    def test_pass_good_observe(self) -> None:
        r = _run(GOOD)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_fail_missing_fields(self) -> None:
        r = _run({"phase": "map"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing:hypothesis", r.stderr)

    def test_fail_cloud_lt_2(self) -> None:
        bad = dict(GOOD)
        bad["cloud_cross"] = ["src-nvd"]
        r = _run(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("cloud_cross:need_ge_2", r.stderr)

    def test_fail_high_risk_with_gap_card(self) -> None:
        bad = dict(GOOD)
        bad["card_id"] = "GAP:no-local-playbook"
        bad["action_class"] = "exploit"
        r = _run(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("high_risk_blocked", r.stderr)

    def test_fail_fuzzy_evidence(self) -> None:
        bad = dict(GOOD)
        bad["evidence_gate"] = "感覺像可以"
        r = _run(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("evidence_gate:not_concrete", r.stderr)

    def test_skill_wires_local_sense(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("references/local-sense.md", text)
        self.assertIn("references/cloud-sources.md", text)
        self.assertIn("sense_gate.py", text)
        self.assertIn("方法／證據門", text)
        self.assertIn("禁止為 Route 建立**手法** playbook", text)

    def test_refs_exist(self) -> None:
        self.assertTrue(LOCAL_SENSE.is_file())
        self.assertTrue(CLOUD.is_file())
        for name in CARD_FILES:
            self.assertTrue((CARDS / name).is_file(), name)

    def test_sense_vault_map_lists_all_cards(self) -> None:
        mapp = ROOT.parent / "references" / "sense-vault-map.md"
        self.assertTrue(mapp.is_file())
        text = mapp.read_text(encoding="utf-8")
        for name in CARD_FILES:
            self.assertIn(name, text)
            body = (CARDS / name).read_text(encoding="utf-8")
            self.assertTrue(body.startswith("# "), name)
            self.assertIn("何時用", body)
            self.assertNotRegex(body, r"(?i)\b(exploit\s+poc|msfvenom|/bin/bash -i)\b")

    def test_pass_challenge_board_card(self) -> None:
        good = dict(GOOD)
        good["card_id"] = "challenge-board-handoff"
        good["hypothesis"] = "挑戰盤已入 HAVE，須交可稽核下一階而非再觀察"
        good["evidence_gate"] = "戰情已列至少一筆挑戰名稱或 id 與觀測來源"
        good["dead_if"] = "指揮拒批挑戰向與管理面 → DEAD:await-cmd-auditable-next"
        r = _run(good)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_pass_session_break_rebuild_card(self) -> None:
        good = dict(GOOD)
        good["card_id"] = "session-break-rebuild"
        good["hypothesis"] = "remount 後舊工作階段不可假設有效"
        good["evidence_gate"] = "已記錄斷裂時刻與舊 token／cookie 失效跡象"
        good["dead_if"] = "重建連續失敗且無重註冊授權 → DEAD:session-unrebuilt"
        r = _run(good)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_pass_web_app_evidence_ladder_card(self) -> None:
        good = dict(GOOD)
        good["card_id"] = "web-app-evidence-ladder"
        good["hypothesis"] = "公開盤齊後須沿達標證據階梯交班"
        good["evidence_gate"] = "已有公開 API 或挑戰盤列表入戰情"
        good["dead_if"] = "無挑戰盤且無管理面線索 → 換面不硬開利用"
        r = _run(good)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
