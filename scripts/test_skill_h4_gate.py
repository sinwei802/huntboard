#!/usr/bin/env python3
"""Read the shipped SKILL.md H-block. Do not reimplement the gate."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"


def _h_block(text: str) -> str:
    m = re.search(
        r"^## 戰役.*?(?=^## )",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not m:
        raise AssertionError("shipped SKILL.md has no 戰役 H-block")
    return m.group(0)


class ShippedH4GateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.h = _h_block(cls.skill)

    def test_reads_shipped_skill_md(self) -> None:
        self.assertTrue(SKILL.is_file(), f"missing shipped skill: {SKILL}")
        self.assertIn("**H4**", self.h)

    def test_new_fact_completes_same_executor_gap_first(self) -> None:
        self.assertIn("新事實先補上一刀還缺的能力", self.h)
        self.assertIn("同一執行者／同一物件", self.h)
        self.assertIn("不得先另開執行者或另一寫入面", self.h)

    def test_stay_on_existing_executor_until_missing_names_observed(self) -> None:
        self.assertIn("next_probe` 的執行者必須是那個行程", self.h)
        self.assertIn("含載入器", self.h)
        self.assertRegex(self.h, r"靜態分析")
        self.assertRegex(self.h, r"DESIGN 搜尋")
        self.assertIn("scoped 否證", self.h)
        self.assertIn("換執行者或覆寫已標成主邏輯的舊檔＝非法下一探", self.h)

    def test_no_windows_is_not_a_close(self) -> None:
        self.assertIn("沒有原生 Windows 執行環境不是關閉", self.h)
        self.assertIn("也不是換執行者的理由", self.h)

    def test_hollow_naming_oneliner_retired(self) -> None:
        old = (
            "未點名「誰已經打開該目錄」與「它查找但不存在的名字」之前，"
            "不得把覆寫已存在主檔、或對該目錄做 HTTP 執行"
        )
        self.assertNotIn(old, self.skill)
        self.assertNotIn("消費者與缺名點了沒", self.skill)
        # 點名 alone must not be the unlock sitting on H4
        h4 = re.search(r"\*\*H4\*\*.*", self.h)
        self.assertIsNotNone(h4)
        self.assertNotIn("未點名", h4.group(0))


if __name__ == "__main__":
    unittest.main()
