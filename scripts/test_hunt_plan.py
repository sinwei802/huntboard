#!/usr/bin/env python3
"""Drive the shipped hunt_plan.py entry points. No reimplementation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import hunt_plan  # noqa: E402


COMPLETE_PLAN = """\
# Hunt Plan
phase: EXECUTE
goal: 取得具名域身份
have: anonymous FTP + unauth HTTP
next_probe: 389 LDAP rootDSE
attempts: 0
untested: Kerberos 預認證
adjust: stay
wildcard: CA web 未 fingerprint
materials: read
last_expected: naming context 或明確拒絕
last_observed:

surface.transport: seen
surface.identity_unauth: seen
surface.naming: seen
surface.materials: seen

bet.H-1.rank: 1
bet.H-1.claim: 未認證目錄可洩漏主體
bet.H-1.probe: 389 LDAP rootDSE
bet.H-1.expect: naming context 或明確拒絕
bet.H-1.kill_if: 連線不可達
bet.H-1.status: active

bet.H-2.rank: 2
bet.H-2.claim: 匿名檔案仍有未讀身份線索
bet.H-2.probe: 重讀 FTP 留下的設定檔找帳號
bet.H-2.expect: 帳號或連線字串
bet.H-2.kill_if: 檔案無身份材料
bet.H-2.status: active
"""

INCOMPLETE_PLAN = """\
# Hunt Plan
phase: OBSERVE
goal:
have:
next_probe:
attempts: 0
untested: 全部
adjust: stay
wildcard:
materials: unread

surface.transport: seen
surface.identity_unauth: untested
surface.naming: untested
surface.materials: untested
"""


class HuntPlanModuleTest(unittest.TestCase):
    def test_observation_complete_requires_have_and_all_surfaces(self) -> None:
        incomplete = hunt_plan.parse_hunt_plan(INCOMPLETE_PLAN)
        self.assertFalse(hunt_plan.observation_complete(incomplete))
        gaps = hunt_plan.observation_gaps(incomplete)
        self.assertIn("have", gaps)
        self.assertIn("surface.identity_unauth", gaps)
        self.assertIn("surface.naming", gaps)

        complete = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)
        self.assertTrue(hunt_plan.observation_complete(complete))
        self.assertEqual(hunt_plan.observation_gaps(complete), [])

    def test_deep_act_blocked_until_observe_and_plan(self) -> None:
        incomplete = hunt_plan.parse_hunt_plan(INCOMPLETE_PLAN)
        self.assertFalse(hunt_plan.allows_deep_act(incomplete, "exploit"))
        self.assertTrue(hunt_plan.allows_deep_act(incomplete, "observe"))
        self.assertFalse(hunt_plan.allows_design_search(incomplete))

        designed = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)
        self.assertTrue(hunt_plan.allows_deep_act(designed, "exploit"))
        self.assertTrue(hunt_plan.allows_deep_act(designed, "auth_use"))

        designed.phase = "DESIGN"
        self.assertFalse(hunt_plan.allows_deep_act(designed, "exploit"))
        self.assertTrue(hunt_plan.allows_design_search(designed))

    def test_adjust_kills_bet_and_promotes_next(self) -> None:
        plan = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)
        updated = hunt_plan.apply_adjust(plan, "bet_killed", "LDAP 連線被 RST")
        self.assertEqual(updated.adjust, "next-bet")
        self.assertEqual(updated.phase, "EXECUTE")
        self.assertEqual(updated.next_probe, "重讀 FTP 留下的設定檔找帳號")
        self.assertEqual(updated.bets[0].status, "killed")
        self.assertEqual(updated.bets[1].status, "active")
        self.assertEqual(plan.bets[0].status, "active")  # original not mutated

        last = hunt_plan.apply_adjust(updated, "bet_killed", "檔案無帳號")
        self.assertEqual(last.adjust, "stall")
        self.assertEqual(last.phase, "ADJUST")
        self.assertEqual(last.next_probe, "")
        self.assertTrue(all(bet.status == "killed" for bet in last.bets))

    def test_adjust_other_outcomes(self) -> None:
        plan = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)

        gained = hunt_plan.apply_adjust(plan, "fact_gained", "rootDSE 回 namingContexts")
        self.assertEqual(gained.phase, "EXECUTE")
        self.assertEqual(gained.adjust, "stay")
        self.assertEqual(gained.attempts, 0)

        surface = hunt_plan.apply_adjust(plan, "new_surface", "新 vhost 出現")
        self.assertEqual(surface.phase, "OBSERVE")
        self.assertEqual(surface.adjust, "re-observe")

        unknown = hunt_plan.apply_adjust(plan, "unknown_primitive", "陌生控制面")
        self.assertEqual(unknown.phase, "DESIGN")
        self.assertEqual(unknown.adjust, "re-design")

        goal = hunt_plan.apply_adjust(plan, "goal_achieved", "拿到域使用者")
        self.assertEqual(goal.phase, "DESIGN")
        self.assertEqual(goal.next_probe, "")

        done = hunt_plan.apply_adjust(plan, "engagement_done", "root.txt")
        self.assertEqual(done.phase, "SUCCESS")
        self.assertEqual(done.adjust, "success")

    def test_stance_roundtrip_and_legacy_parse(self) -> None:
        plan = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)
        line = hunt_plan.render_stance_line(plan)
        self.assertTrue(line.startswith("態勢：Phase=EXECUTE"))
        self.assertIn("Goal=取得具名域身份", line)
        self.assertIn("主賭=H-1 未認證目錄可洩漏主體", line)
        fields = hunt_plan.parse_stance_line(line)
        rebuilt = hunt_plan.stance_to_plan(fields)
        self.assertEqual(rebuilt.phase, "EXECUTE")
        self.assertEqual(rebuilt.goal, "取得具名域身份")
        self.assertEqual(rebuilt.next_probe, "389 LDAP rootDSE")

        legacy = "態勢：Goal=辨識傳輸面暴露 · attempts=1 · 未測軸=內容/命名 · wildcard=無"
        legacy_fields = hunt_plan.parse_stance_line(legacy)
        self.assertEqual(legacy_fields["Goal"], "辨識傳輸面暴露")
        self.assertEqual(legacy_fields["attempts"], "1")
        legacy_plan = hunt_plan.stance_to_plan(legacy_fields)
        self.assertEqual(legacy_plan.goal, "辨識傳輸面暴露")
        self.assertEqual(legacy_plan.attempts, 1)

    def test_opening_intent_splits_transport_from_remainder(self) -> None:
        self.assertEqual(
            hunt_plan.opening_intent(
                "開局掃 10.10.11.23",
                ports_known=False,
                observe_complete_flag=False,
            ),
            "observe_transport",
        )
        self.assertEqual(
            hunt_plan.opening_intent(
                "進行作戰，先掃描",
                ports_known=True,
                observe_complete_flag=False,
            ),
            "observe_remainder_batch",
        )
        self.assertEqual(
            hunt_plan.opening_intent(
                "可以，繼續",
                ports_known=True,
                observe_complete_flag=False,
            ),
            "named_step",
        )
        self.assertEqual(
            hunt_plan.opening_intent(
                "掃一下漏的 UDP",
                ports_known=True,
                observe_complete_flag=True,
            ),
            "named_step",
        )

    def test_validate_execute_requires_bets(self) -> None:
        plan = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)
        self.assertEqual(hunt_plan.validate_hunt_plan(plan), [])
        plan.bets = []
        errors = hunt_plan.validate_hunt_plan(plan)
        self.assertTrue(any("active bet" in item for item in errors))

    def test_unknown_outcome_and_kind_are_errors(self) -> None:
        plan = hunt_plan.parse_hunt_plan(COMPLETE_PLAN)
        with self.assertRaises(hunt_plan.HuntPlanError):
            hunt_plan.apply_adjust(plan, "try_harder", "x")
        with self.assertRaises(hunt_plan.HuntPlanError):
            hunt_plan.is_deep_act("kerberoast")


class HuntPlanCliTest(unittest.TestCase):
    def _run(self, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "hunt_plan.py"), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def test_cli_validate_adjust_allows_deep_opening(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hunt-plan.md"
            path.write_text(COMPLETE_PLAN, encoding="utf-8")

            ok = self._run("validate", str(path))
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertIn("OK phase=EXECUTE deep_act=True", ok.stdout)
            self.assertIn("態勢：Phase=EXECUTE", ok.stdout)

            blocked = self._run("allows-deep", str(path), "--kind", "exploit")
            self.assertEqual(blocked.returncode, 0, blocked.stderr)
            self.assertEqual(blocked.stdout.strip(), "yes")

            adjusted = self._run(
                "adjust",
                str(path),
                "--outcome",
                "bet_killed",
                "--observed",
                "LDAP RST",
            )
            self.assertEqual(adjusted.returncode, 0, adjusted.stderr)
            self.assertIn("phase: EXECUTE", adjusted.stdout)
            self.assertIn("adjust: next-bet", adjusted.stdout)
            self.assertIn("status: killed", adjusted.stdout)
            # CLI does not write unless --write
            on_disk = hunt_plan.load_hunt_plan(path)
            self.assertEqual(on_disk.bets[0].status, "active")

            written = self._run(
                "adjust",
                str(path),
                "--outcome",
                "bet_killed",
                "--observed",
                "LDAP RST",
                "--write",
            )
            self.assertEqual(written.returncode, 0, written.stderr)
            on_disk = hunt_plan.load_hunt_plan(path)
            self.assertEqual(on_disk.adjust, "next-bet")
            self.assertEqual(on_disk.bets[0].status, "killed")

            path.write_text(INCOMPLETE_PLAN, encoding="utf-8")
            no = self._run("allows-deep", str(path), "--kind", "exploit")
            self.assertEqual(no.returncode, 2)
            self.assertIn("no", no.stdout)
            self.assertIn("gap:have", no.stdout)

            opening = self._run("opening", "開局掃 10.10.11.1")
            self.assertEqual(opening.returncode, 0, opening.stderr)
            opening_lines = opening.stdout.splitlines()
            self.assertEqual(opening_lines[0], "observe_transport")
            self.assertTrue(opening_lines[1].startswith("loaded="), opening.stdout)

            remainder = self._run(
                "opening", "開局掃 10.10.11.1", "--ports-known"
            )
            self.assertEqual(remainder.stdout.splitlines()[0], "observe_remainder_batch")


class SessionLoadTest(unittest.TestCase):
    def _env(self, tmp: str, session: str | None) -> dict[str, str]:
        env = {
            "HUNTSPEAR_SESSION_LOAD_DIR": tmp,
            "PATH": os.environ.get("PATH", ""),
        }
        if session is not None:
            env["HUNTSPEAR_SESSION_ID"] = session
        return env

    def test_mark_show_stale_reset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, self._env(tmp, "sess-test"), clear=True):
                self.assertEqual(hunt_plan.format_loaded_line(), "loaded=")
                marked = hunt_plan.mark_session_load(
                    ["hunt-loop", "execution-contract"]
                )
                self.assertEqual(marked, "loaded=execution-contract,hunt-loop")
                path = Path(tmp) / "sess-test.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                data["loaded"]["hunt-loop"]["sha256"] = "0" * 64
                path.write_text(json.dumps(data), encoding="utf-8")
                line = hunt_plan.format_loaded_line()
                self.assertIn("loaded=execution-contract", line)
                self.assertIn("stale=hunt-loop", line)
                self.assertNotIn("loaded=hunt-loop", line)
                self.assertEqual(hunt_plan.reset_session_load(), "loaded=")
                self.assertFalse(path.exists())

    def test_absent_session_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, self._env(tmp, None), clear=True):
                self.assertEqual(
                    hunt_plan.format_loaded_line(), "loaded= session=absent"
                )
                self.assertEqual(
                    hunt_plan.mark_session_load(["hunt-loop"]), "session=absent"
                )
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_unknown_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, self._env(tmp, "sess-test"), clear=True):
                with self.assertRaises(hunt_plan.HuntPlanError):
                    hunt_plan.mark_session_load(["../SKILL"])
                with self.assertRaises(hunt_plan.HuntPlanError):
                    hunt_plan.mark_session_load(["not-a-real-ref"])

    def test_cli_mark(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "hunt_plan.py"),
                    "session-load",
                    "mark",
                    "hunt-loop",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=self._env(tmp, "cli-sess"),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "loaded=hunt-loop")


class LoaderSelfTest(unittest.TestCase):
    def test_loader_self_test_and_overlay_path(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "load_state_bundle.py"), "--self-test"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("PASS:", proc.stdout)
        self.assertIn("overlay", proc.stdout)


class SkillContractTest(unittest.TestCase):
    """The markdown skill must encode the hunter loop and must not pin tactics."""

    ROOT = SCRIPTS.parent

    def _read(self, relative: str) -> str:
        return (self.ROOT / relative).read_text(encoding="utf-8")

    def test_skill_has_hunter_cards_and_keeps_red_lines(self) -> None:
        skill = self._read("SKILL.md")
        for token in ("H1", "H2", "H3", "OBSERVE", "DESIGN", "EXECUTE", "ADJUST"):
            self.assertIn(token, skill)
        self.assertIn("一則使用者訊息 = 一個已授權方向", skill)
        self.assertIn("新發現／同輪取得的材料不是新授權", skill)
        self.assertIn("hunt-loop.md", skill)
        self.assertNotIn("必須先 Kerberoast", skill)
        self.assertNotIn("做完 ESC1", skill)
        # Print-optional: truth required, tables not required each turn.
        self.assertNotIn("沒有這四行就不得碰目標", skill)
        self.assertNotIn("缺卡視同未完成", skill)
        self.assertIn("不必印", skill)

    def test_combat_body_has_no_hermes_scoreboard(self) -> None:
        skill = self._read("SKILL.md")
        for banned in (
            "Hermes",
            "huntspear-runtime",
            "7–8/10",
            "6–7/10",
            "p0-runtime-brief",
        ):
            self.assertNotIn(banned, skill)
        self.assertRegex(skill, r"開局|掃|foothold")

    def test_hunt_loop_and_tactical_search_are_search_first(self) -> None:
        loop = self._read("references/hunt-loop.md")
        tactical = self._read("references/tactical-search.md")
        for name in hunt_plan.SURFACE_CLASSES:
            self.assertIn(name, loop)
        self.assertIn("DESIGN", tactical)
        self.assertIn("不是等 Stall 才第一次找戰術", tactical)
        self.assertIn("scripts/hunt_plan.py", loop)
        self.assertNotRegex(tactical, r"必須做完\s*A\s*→\s*E")
        # Taxonomy lookup is a lens, not the first query.
        self.assertIn("禁止把「當前主流分類體系叫什麼」當本回合第一條 query", tactical)
        # Directory / identity observed → DESIGN search keys, not a technique menu.
        self.assertIn("域身份", tactical)
        self.assertIn("不是等 Stall", tactical)
        self.assertNotIn("必須先 Kerberoast", tactical)
        self.assertNotIn("做完 ESC1", tactical)
        self.assertNotRegex(tactical, r"ESC1|ESC4|ESC7|Kerberoast|certipy find")

    def test_opening_observe_is_not_ports_only(self) -> None:
        loop = self._read("references/hunt-loop.md")
        preflight = self._read("references/htb-preflight.md")
        pipeline = self._read("references/port-scan-pipeline.md")
        self.assertIn("observe_remainder_batch", loop)
        self.assertIn("hunt-loop.md", preflight)
        self.assertIn("hunt-loop.md", pipeline)

    def test_new_viewer_gets_remainder_batch(self) -> None:
        skill = self._read("SKILL.md")
        loop = self._read("references/hunt-loop.md")
        exe = self._read("references/execution-contract.md")
        self.assertIn("新觀看者", skill)
        self.assertIn("只准具名剩餘觀察 batch", skill)
        self.assertIn("### 2.4 新觀看者剩餘觀察", loop)
        self.assertIn("不是第一份到手材料的利用", exe)
        self.assertNotIn("新 identity 是新資產面", skill)
        self.assertNotRegex(loop, r"/opt|sudo -l|linpeas")

    def test_commander_facing_voice_is_not_telegraphic(self) -> None:
        skill = self._read("SKILL.md")
        out = self._read("references/output-contract.md")
        self.assertNotIn("輸出經濟且口語", skill)
        self.assertIn("對指揮說話要好懂", skill)
        self.assertIn("術語第一次出現用人話解釋", skill)
        self.assertIn("## 1.1 對指揮的用語", out)
        self.assertIn("先人話，再術語", out)
        self.assertIn("一句一事", out)
        self.assertIn("停在能複述", out)
        self.assertIn("用自己的話複述", out)
        self.assertIn("台灣口語繁中", skill)
        self.assertIn("翻譯腔骨架", skill)
        self.assertIn("單字本身不禁", skill)
        self.assertIn("只約束講給指揮聽的正文", out)
        self.assertIn("禁骨架，不禁單字", out)
        self.assertIn("445 開著，是 SMB", out)
        self.assertNotIn("展開見 `thinking-loop.md`", skill)
        self.assertNotIn("輸出前逐條默想", out)

    def test_scan_results_are_obsidian_tables(self) -> None:
        skill = self._read("SKILL.md")
        out = self._read("references/output-contract.md")
        pipeline = self._read("references/port-scan-pipeline.md")
        self.assertIn("可列舉掃描結果", skill)
        self.assertIn("Obsidian", skill)
        self.assertIn("程式碼區塊", skill)
        self.assertIn("禁止只渲染表", skill)
        self.assertIn("## 1.2 可列舉掃描結果用表", out)
        self.assertIn("**必須**用 code fence", out)
        self.assertIn("禁止回「去開某個 md」", out)
        self.assertIn("先區塊、後選項欄", pipeline)
        self.assertIn("markdown` code fence", pipeline)
        self.assertIn("禁止只渲染表", pipeline)

    def test_user_commands_live_in_code_fences(self) -> None:
        skill = self._read("SKILL.md")
        out = self._read("references/output-contract.md")
        exe = self._read("references/execution-contract.md")
        self.assertIn("需要指揮執行的指令一律放進 code fence", skill)
        self.assertIn("## 1.3 互動：指揮要跑的指令", out)
        self.assertIn("**全部**放進 code fence", out)
        self.assertIn("禁止只用行內 backtick 當交付", out)
        self.assertIn("需要指揮執行的指令**全部**放進獨立 code fence", exe)

    def test_declared_name_hosts_handoff_is_user(self) -> None:
        skill = self._read("SKILL.md")
        preflight = self._read("references/htb-preflight.md")
        loop = self._read("references/hunt-loop.md")
        pipeline = self._read("references/port-scan-pipeline.md")
        self.assertIn("本機 vantage 交給指揮", skill)
        self.assertIn("禁止用只打 IP 或改 Host 標頭當「就不必請指揮加 hosts」", skill)
        self.assertIn("禁止改走未點名的 Proxy／curl 當「就不必等指揮」", skill)
        self.assertIn("這是指揮的活", preflight)
        self.assertNotIn("再建議補 hosts", preflight)
        self.assertIn("下一步先是 `[USER]` 加 hosts", loop)
        self.assertIn("禁止先交 Host 標頭剩餘觀察來跳過指揮", loop)
        self.assertIn("下一步是 `[USER]` 加 hosts", pipeline)

    def test_handoff_is_ranked_options_not_yes_no(self) -> None:
        skill = self._read("SKILL.md")
        out = self._read("references/output-contract.md")
        loop = self._read("references/hunt-loop.md")
        self.assertIn("必須交 2–3 條已排序選項", skill)
        self.assertIn("[建議]", skill)
        self.assertIn("只確認選項 1", skill)
        self.assertIn("禁止只交是非題", skill)
        self.assertIn("禁止把未完成觀察攤成請指揮發明的選單", skill)
        self.assertIn("建議那一條", skill)
        self.assertIn("保存完停在態勢，不交下一刀選項", skill)
        self.assertIn("禁止只交「回打或繼續」的是非題", out)
        self.assertIn("checkpoint 保存完", out)
        self.assertIn("標為建議的那一條", loop)
        self.assertNotIn("回「打」或「繼續」我就只跑這一刀", skill)

    def test_warboard_apply_is_combat_path(self) -> None:
        skill = self._read("SKILL.md")
        schemas = self._read("references/state-schemas.md")
        index = self._read("references/tradecraft-index.md")
        war = self._read("references/warboard-schema.md")
        self.assertIn("warboard.py", skill)
        self.assertIn("--print-schema", skill)
        self.assertIn("禁止手寫核心檔", skill)
        self.assertIn("負債", schemas)
        self.assertIn("不是戰鬥寫入器", schemas)
        self.assertIn("warboard.py apply", index)
        self.assertIn("唯一真源", war)
        self.assertNotIn("checkpoint_write.py", skill)
        self.assertNotIn("stamp 失敗才讀", skill)
        self.assertNotIn("先把事實寫進五核心檔正文，再跑", skill)

    def test_cheapest_probe_is_goal_not_current_auth(self) -> None:
        skill = self._read("SKILL.md")
        loop = self._read("references/hunt-loop.md")
        out = self._read("references/output-contract.md")
        self.assertIn("不是以留在已批准的動作類裡計", skill)
        self.assertIn("禁止只交低權限變體或只繼續解當前身份的下一把鑰匙", skill)
        self.assertIn("提出≠執行", skill)
        self.assertIn("未使用的秘密", skill)
        self.assertIn("受約束執行者", skill)
        self.assertIn("必須寫進選項並可當建議", skill)
        self.assertIn("禁止只交低權限變體", skill)
        self.assertIn("不是看能不能留在已批准的動作類裡", loop)
        self.assertIn("禁止改交排序第二的同權限變體", loop)
        self.assertIn("只給低權限變體", out)
        self.assertIn("未使用的秘密", loop)

    def test_recon_matrix_is_one_direction(self) -> None:
        skill = self._read("SKILL.md")
        loop = self._read("references/hunt-loop.md")
        exe = self._read("references/execution-contract.md")
        self.assertIn("偵查矩陣一次做完", skill)
        self.assertIn("同一 expect／kill_if 的變體不是新方向", skill)
        self.assertNotIn("## 11. References", skill)
        self.assertIn("### 4.1 一條賭注的偵查是矩陣，不是現場試錯", loop)
        self.assertIn("矩陣跑完才 HANDOFF", loop)
        self.assertIn("一張偵查矩陣", exe)
        self.assertIn("只是 illustration，不是唯一形", loop)
        self.assertIn("argv、旗標、路徑、mode", skill)

    def test_experiment_needs_signal_and_readable_errors(self) -> None:
        skill = self._read("SKILL.md")
        loop = self._read("references/hunt-loop.md")
        self.assertIn("每格成立與失敗必須能分開", skill)
        self.assertIn("分不開＝未決", skill)
        self.assertIn("錯誤可讀處迭代", skill)
        self.assertIn("沒有現成重現環境不要停下來搭實驗室", skill)
        self.assertIn("本地命中≠目標命中", skill)
        self.assertIn("解讀已拉回材料的工具預設打手側", skill)
        self.assertIn("不把「在目標安裝客戶端」當下一探", skill)
        self.assertIn("文章 payload 是假設來源", skill)
        self.assertNotIn("註解／終結符家族", skill)
        self.assertNotIn("ORDER BY", skill)
        self.assertNotIn("kill_if 未決", skill)
        self.assertIn("不把分不開的觀測寫成已否證", skill)
        self.assertIn("允許少量探測去發現觀測已塌縮", loop)
        self.assertIn("禁止把塌縮觀測上的家族掃完當成矩陣做完", loop)
        self.assertIn("具名符號家族（如註解符）是 illustration", loop)
        self.assertIn("不為這條去搭實驗室", loop)
        self.assertIn("不得是 `bet_killed`", loop)

    def test_goal_is_capability_not_product_cve(self) -> None:
        skill = self._read("SKILL.md")
        loop = self._read("references/hunt-loop.md")
        hyp = self._read("references/hypothesis-engine.md")
        self.assertIn("Goal 是能力，不是產品洞", skill)
        self.assertIn("同一產品的姊妹 CVE／再一支檢測腳本", skill)
        self.assertIn("禁止產品+CVE 當 Goal", loop)
        self.assertIn("同一產品的姊妹 CVE", hyp)
        self.assertIn("視同沒有下一注", loop)


if __name__ == "__main__":
    unittest.main()
