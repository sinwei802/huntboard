# 操作者說明（偏好，不是戰鬥閘）

本檔給人讀；agent 以 [`SKILL.md`](SKILL.md) 為準。產品名 **HuntSpear**；倉庫 https://github.com/sinwei802/huntspear。內部物件 `warboard`（作戰台）維持英文技術名。

## 如何載入

- 把本目錄當成 `$SKILL_ROOT`（必須含 `SKILL.md`、`references/`、`scripts/`）。
- 用 symlink 把同一棵樹掛進 agent harness；不要 fork 複製。
- 開局熱路徑：
  1. `python3 "$SKILL_ROOT/scripts/warboard.py" opening "…"`
  2. `python3 "$SKILL_ROOT/scripts/hunt_plan.py" opening "…"`
  3. `python3 "$SKILL_ROOT/scripts/sense_gate.py" --db ./pentest-state/warboard.sqlite --action observe`
- 唯一真源：`./pentest-state/warboard.sqlite`。寫入用 `warboard.py apply --facts <json>`。
- 高風險下一刀前再跑 `sense_gate.py --db … --action exploit`（可加 `--check proposal.json`）。fail＝不准出利用級選項。閘門讀庫，不信提案自述。
- 舊 markdown 五核心檔（`asset-graph.md` 等）是負債。開局只會警告 `markdown_debt=… unused`，不當 HAVE。

## warboard console（可選）

- 若你有本地 warboard（作戰台）console，指向你的 engagement SQLite（`./pentest-state/warboard.sqlite`）。
- Schema／互動契約：`references/warboard-schema.md`、`references/interaction-truth-contract.md`（不必每回合讀）。

## 離線破解偏好（可選）

- 攻擊主機若無 GPU，不要在那台上跑 hashcat／john。
- 把離線 hash 依你自己的路徑慣例拷到 GPU 機；同時在 `./pentest-state/loot/` 留一份。
- 只把檔名與相對提示交給人——**不要**假設另一台機器的絕對掛載路徑。
- 本節只談偏好與搬運，**不**含破解步驟或字典／規則 cookbook。

## 紅線

- 本樹無 PoC、payload、逐步利用食譜；操作者也不應要求 agent 把這類內容寫進 skill。
- markdown bundle 不要再當本期前提。

---

## English (short)

Operator preferences (not combat gates). Opening path: `warboard.py opening` → `hunt_plan.py opening` → `sense_gate.py --db`. Sole truth is `./pentest-state/warboard.sqlite`. Markdown core files are unused debt. Prefer offline cracking on a GPU box (paths/hints only). Red line: no PoC / payload / exploit cookbook.
