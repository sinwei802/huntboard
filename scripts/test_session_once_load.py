#!/usr/bin/env python3
"""Read shipped load-gate text. Do not reimplement the gate."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class SessionOnceLoadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = _read("SKILL.md")
        cls.exe = _read("references/execution-contract.md")
        cls.loop = _read("references/hunt-loop.md")
        cls.out = _read("references/output-contract.md")
        cls.think = _read("references/thinking-loop.md")
        cls.index = _read("references/tradecraft-index.md")
        cls.pipeline = _read("references/port-scan-pipeline.md")

    def test_session_load_list_is_mechanical(self) -> None:
        self.assertIn("loaded=<短名>", self.skill)
        self.assertIn("session-load mark", self.skill)
        self.assertIn("session-load reset", self.skill)
        self.assertIn("session=absent", self.skill)
        self.assertIn("stale=", self.skill)
        self.assertIn("名單不進 `./pentest-state/`", self.skill)
        self.assertIn("hunt-plan 只印態勢列、缺口、活躍賭注", self.skill)
        schemas = _read("references/state-schemas.md")
        self.assertIn("brief 不倒正文", schemas)
        self.assertNotIn("有則 loader 一併印出", schemas)

    def test_skill_md_is_session_once(self) -> None:
        self.assertIn("本場已注入的 `SKILL.md` 禁止再 `read_file`", self.skill)
        self.assertIn("只執行、不讀源碼", self.skill)
        self.assertIn("同一相對路徑本場已讀過", self.skill)
        self.assertIn("禁止再讀另一個 harness 的同套件路徑", self.skill)
        self.assertNotIn("即將 ACT／可執行命令／高風險確認", self.skill)

    def test_scripts_are_run_not_read(self) -> None:
        self.assertIn("hunt_plan.py\" opening", self.skill)
        self.assertIn("禁止 `read_file` 其源碼", self.skill)
        self.assertIn("loader 預設摘要", self.skill)
        self.assertIn("`--full` 才倒核心檔正文", self.skill)
        self.assertIn("checkpoint_write.py", self.skill)
        self.assertIn("禁止手寫核心檔", self.skill)
        self.assertIn("禁止為對格式讀 schema 或腳本源碼", self.skill)
        self.assertNotIn('--stamp ./pentest-state', self.skill)

    def test_source_first_is_this_engagement(self) -> None:
        self.assertIn("本場**已取回", self.skill)
        self.assertIn("不是舊案、不是整個磁碟", self.skill)
        self.assertIn("大檔先 grep／摘要", self.skill)
        self.assertNotIn("目前可及的來源", self.skill)

    def test_execution_contract_is_not_per_act(self) -> None:
        self.assertIn("每個 session 最多讀 1 次", self.exe)
        self.assertIn("開局觀察／fingerprint 不必讀", self.exe)
        self.assertIn("動作類升級，或要出高風險 CONFIRM 卡", self.exe)
        self.assertNotIn("ACT 前若本輪尚未讀過本文件，必須先讀", self.exe)
        self.assertNotIn("ACT 前必讀", self.index)
        self.assertIn("載入時機見該檔開頭", self.think)
        self.assertNotIn("未讀則先讀", self.think)
        self.assertIn("載入時機見該檔開頭", self.pipeline)

    def test_ioc_lookup_is_not_opening_ritual(self) -> None:
        start = self.skill.index("每次啟動")
        end = self.skill.index("腳本只執行")
        ritual = self.skill[start:end]
        self.assertNotIn("ioc_lookup.py", ritual)
        self.assertNotIn("evidence-db", ritual)
        self.assertNotIn("開局查證據資料庫", self.skill)
        self.assertIn("第一次見到可索引 IOC", self.skill)
        self.assertIn("ioc_lookup.py", self.skill)
        self.assertIn("0 次讀 vault", self.skill)
        self.assertIn("禁止 `read_file` vault", self.skill)
        self.assertIn("寫庫只在收尾", self.skill)
        self.assertIn("這三步不含查庫", self.skill)
        self.assertIn("禁止跑 `ioc_lookup.py`", self.skill)
        self.assertIn("收尾時才載 `evidence-db`", self.skill)
        self.assertNotIn("用 `evidence-db` 的總索引查一次", self.skill)

    def test_screenshots_are_paths_not_ingest(self) -> None:
        self.assertIn("HANDOFF 只給路徑", self.skill)
        self.assertIn("禁止 `read_file` 圖進模型", self.skill)
        self.assertNotIn("給指揮看圖", self.skill)
        self.assertIn("檔案落地即完成觀察", self.loop)
        self.assertNotIn("對話內嵌該路徑", self.loop)
        self.assertNotIn("必須內嵌", self.out)
        self.assertIn("禁止把圖灌進模型", self.out)

    def test_phase_boundary_suggests_compact(self) -> None:
        self.assertIn("`/compact` 或 `/new`", self.skill)
        self.assertIn("不代跑", self.skill)

    def test_r2_blocks_secrets_not_named_research(self) -> None:
        self.assertIn("禁止同回合**使用**", self.skill)
        self.assertIn("即使當則方向已點名 auth_use", self.skill)
        self.assertIn("同回合可以搜「怎麼做」", self.skill)
        self.assertNotIn("新拿到的只是其參數", self.skill)

    def test_upgrade_does_not_override_open_h4(self) -> None:
        self.assertIn("升級不得取代 `next_probe`", self.skill)
        self.assertIn("H4 未關的寫入注仍鎖執行者", self.skill)

    def test_stall_trigger_is_outcome_enum(self) -> None:
        self.assertIn("outcome 皆非 `fact_gained`／`new_surface`", self.skill)
        self.assertNotIn("無新重要事實", self.skill)

    def test_foothold_handoff_is_direction_not_end(self) -> None:
        self.assertIn("這是換方向、不是收工", self.exe)
        self.assertIn("HANDOFF 結束的是方向不是狩獵", self.exe)

    def test_commander_stance_omits_phase(self) -> None:
        self.assertIn("態勢：Goal=… · 下一探=<建議那條的短名>", self.skill)
        self.assertIn("Phase 只寫進", self.skill)
        self.assertIn("不印給指揮", self.out)
        self.assertNotIn("態勢：Phase=… · Goal=… · 下一探=…", self.skill)

    def test_unequal_stall_has_one_canonical_home(self) -> None:
        self.assertEqual(self.skill.count("不等 Stall"), 1)
        self.assertIn("觸發見 H2", self.skill)


if __name__ == "__main__":
    unittest.main()
