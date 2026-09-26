# HuntSpear

**HuntSpear**（狩獵矛）是授權狩獵用的薄方法／證據門 skill——**不是**攻擊 cookbook。

本倉庫是開源方法論層：本地 sense、薄方法卡（證據門、交班、死路），以及機械式 `sense_gate`。**不**附帶 payload、PoC，也**不**提供逐步利用食譜。

- 產品名：**HuntSpear**
- 倉庫：https://github.com/sinwei802/huntspear
- 內部物件 `warboard`（作戰台／共用狀態真源）維持英文技術名；本 README 僅此處附一次繁中 gloss。

## 安裝

### Clone

```bash
git clone https://github.com/sinwei802/huntspear.git
```

### Grok Bot

```bash
ln -sfn /path/to/huntspear /home/box/agent-data/workflows/huntspear
```

然後在對話中選 `huntspear`（`/` 或 `@`），或依 skill 描述觸發。

### Generic / Claude

將 `$SKILL_ROOT` 指到 clone 根目錄（必須含 `SKILL.md`、`references/`、`scripts/`），再載入 `SKILL.md`。優先用 symlink 進 harness；不要分叉複製整棵樹。

```bash
export SKILL_ROOT="$(pwd)/huntspear"
```

### 驗證

```bash
cd scripts && python3 -m unittest discover -p 'test_*.py'
```

## 從這裡開始

| 路徑 | 角色 |
|------|------|
| [`SKILL.md`](SKILL.md) | Agent skill 入口＋漸進揭露 |
| [`references/sense-cards/`](references/sense-cards/) | 薄方法／證據門卡 |
| [`scripts/sense_gate.py`](scripts/sense_gate.py) | 機械提案閘（僅方法論） |
| [`USER.md`](USER.md) | 操作者載入說明（非戰鬥閘） |
| [`CHANGELOG.md`](CHANGELOG.md) | 滾動變更紀錄 |

## 紅線（必須遵守）

- **禁止**在本 skill／本 repo 放 PoC、payload、exploit cookbook，或逐步攻擊食譜。
- 方法卡只寫：何時用、要驗證什麼、證據長什麼樣、死路、去哪查——**不**寫怎麼打穿。
- 授權作業、明確 scope；本樹是副駕駛方法層，不是自動殺傷鏈。

## 目錄結構

```
SKILL.md              # agent skill 入口
USER.md               # 操作者說明
CHANGELOG.md
LICENSE               # MIT（勿改）
references/           # contracts、local-sense、sense-cards、indexes
scripts/              # hunt_plan、sense_gate、helpers、tests
```

## 授權

[MIT](LICENSE) — Copyright (c) 2026 sinwei802.

## 相關

自 [`sinwei802/kali_cc_skills`](https://github.com/sinwei802/kali_cc_skills) 抽出（該 repo 的 `huntspear/` 路徑現為指向此處的 stub）。

---

## English (short)

**HuntSpear** is a thin method / evidence-gate skill for **authorized** hunting — **not** an attack cookbook. It ships local sense, thin method cards, and a mechanical `sense_gate`. It does **not** ship payloads, PoCs, or step-by-step exploit recipes.

- **Install:** `git clone https://github.com/sinwei802/huntspear.git` — set `$SKILL_ROOT` to the clone root (must contain `SKILL.md`, `references/`, `scripts/`), or symlink into your harness.
- **Verify:** `cd scripts && python3 -m unittest discover -p 'test_*.py'`
- **Start here:** `SKILL.md` (agents), `USER.md` (operators), `references/sense-cards/`, `scripts/sense_gate.py`.
- **Red lines:** no PoC / payload / exploit cookbook in this tree. Internal name `warboard` stays English (ops console / shared state); see Traditional Chinese section above for the one-time gloss.
- **License:** [MIT](LICENSE).
