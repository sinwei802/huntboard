#!/usr/bin/env python3
"""Drive shipped ioc_lookup.py. Do not reimplement the lookup."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import ioc_lookup  # noqa: E402

INDEX = """\
# 證據資料庫

## 案件清單

| 案件 | 日期 | 主站 |
|------|------|------|
| [[20260101舊案]] | 2026-01-01 | `evil.example` |

## 實體索引

### 伺服器

| IP | Hostname | 案件 |
|----|----------|------|
| [[伺服器-203.0.113.10]] | box-a | 0101 |
| [[伺服器-198.51.100.20]] | box-b | 0101 |

### 域名

| 域名 | 案件 |
|------|------|
| [[域名-evil.example]] | 0101 |
"""

ENTITY_A = """\
---
title: 伺服器-203.0.113.10
---

# 伺服器-203.0.113.10

## 出現案件
- [[20260101舊案]]

## 關聯實體
- [[域名-evil.example]]

## 備註
SECRET_NOTE_SHOULD_NOT_LEAK
"""

ENTITY_B = """\
---
title: 伺服器-198.51.100.20
---

# 伺服器-198.51.100.20

## 出現案件
- [[20260101舊案]]

## 備註
SECOND_ENTITY_NOTE
"""

CASE_NOTE = """\
# 20260101舊案

CASE_SECRET_SHOULD_NOT_LEAK
"""

FAKE_SKILL = """\
# evidence-db

| 項 | 值 | 覆寫 |
|---|---|---|
| vault | `/tmp/unused-vault` | `OBSIDIAN_VAULT` |
| 資料庫根 | `資安/打詐/證據資料庫/` | — |
| 總索引 | `證據資料庫.md` | 索引 |
| 實體目錄 | `實體/` | 每個 IOC 一個 md |
"""


def _write_tree(root: Path) -> Path:
    db = root / "資安" / "打詐" / "證據資料庫"
    entities = db / "實體"
    entities.mkdir(parents=True)
    (db / "證據資料庫.md").write_text(INDEX, encoding="utf-8")
    (entities / "伺服器-203.0.113.10.md").write_text(ENTITY_A, encoding="utf-8")
    (entities / "伺服器-198.51.100.20.md").write_text(ENTITY_B, encoding="utf-8")
    (root / "資安" / "打詐" / "20260101舊案.md").write_text(
        CASE_NOTE, encoding="utf-8"
    )
    return db / "證據資料庫.md"


class IocLookupTest(unittest.TestCase):
    def test_hit_miss_and_single_entity_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            index = _write_tree(Path(tmp))
            result = ioc_lookup.run_lookup(
                ["203.0.113.10", "10.10.11.1", "198.51.100.20"],
                index_path=index,
            )
            text = result.render()
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.hits, 2)
            self.assertEqual(result.misses, 1)
            self.assertEqual(result.entities, 1)
            self.assertIn("HIT 203.0.113.10", text)
            self.assertIn("MISS 10.10.11.1", text)
            self.assertIn("HIT 198.51.100.20", text)
            self.assertIn("ENTITY 伺服器-203.0.113.10", text)
            self.assertIn("[[20260101舊案]]", text)
            self.assertIn("[[域名-evil.example]]", text)
            self.assertNotIn("ENTITY 伺服器-198.51.100.20", text)
            self.assertNotIn("SECRET_NOTE_SHOULD_NOT_LEAK", text)
            self.assertNotIn("SECOND_ENTITY_NOTE", text)
            self.assertNotIn("CASE_SECRET_SHOULD_NOT_LEAK", text)

    def test_case_list_hit_does_not_open_case_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            index = _write_tree(Path(tmp))
            result = ioc_lookup.run_lookup(
                ["20260101舊案"],
                index_path=index,
            )
            text = result.render()
            self.assertEqual(result.hits, 1)
            self.assertEqual(result.entities, 0)
            self.assertIn("HIT 20260101舊案", text)
            self.assertNotIn("CASE_SECRET_SHOULD_NOT_LEAK", text)
            self.assertNotIn("ENTITY", text)

    def test_no_query_skips_without_index(self) -> None:
        result = ioc_lookup.run_lookup([], index_path=Path("/no/such/index.md"))
        self.assertEqual(result.status, "skip")
        self.assertEqual(result.reason, "no_query")

    def test_short_query_skips(self) -> None:
        result = ioc_lookup.run_lookup(["ab"], index_path=Path("/no/such/index.md"))
        self.assertEqual(result.status, "skip")
        self.assertIn("SKIP ab reason=too_short", result.render())

    def test_missing_index_is_unavailable(self) -> None:
        missing = Path("/no/such/evidence-index.md")
        result = ioc_lookup.run_lookup(["203.0.113.10"], index_path=missing)
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.reason, "index_unreadable")

    def test_cli_exit_zero_on_miss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            index = _write_tree(Path(tmp))
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "ioc_lookup.py"),
                 "--index", str(index), "not-in-db.example"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("status=ok", proc.stdout)
            self.assertIn("MISS not-in-db.example", proc.stdout)

    def test_resolve_from_evidence_db_skill_and_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = _write_tree(root)
            skill = root / "evidence-db" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text(FAKE_SKILL, encoding="utf-8")
            env = os.environ.copy()
            env["EVIDENCE_DB_SKILL"] = str(skill)
            env["OBSIDIAN_VAULT"] = str(root)
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "ioc_lookup.py"), "evil.example"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("HIT evil.example", proc.stdout)
            self.assertTrue(index.is_file())

    def test_parse_shipped_evidence_db_table(self) -> None:
        shipped = None
        for candidate in ioc_lookup.evidence_db_skill_candidates():
            if candidate.is_file():
                shipped = candidate
                break
        if shipped is None:
            self.skipTest("evidence-db skill not installed")
        defaults = ioc_lookup.parse_evidence_db_defaults(
            shipped.read_text(encoding="utf-8")
        )
        self.assertEqual(defaults.get("總索引"), "證據資料庫.md")
        self.assertIn("證據資料庫", defaults.get("資料庫根", ""))
        self.assertTrue(defaults.get("vault"))


if __name__ == "__main__":
    unittest.main()
