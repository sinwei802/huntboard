# HuntSpear skill 交件清單（2026-09-26 夜）

主人起床可驗：本檔 + 下列路徑 + `python3 -m unittest discover -p 'test_*.py'`（`scripts/`）。

## 交件定義（滿意）

| 項 | 狀態 | 驗法 |
|----|------|------|
| A 既有狩獵／R1–R8／H1–H4／hunt_plan | 保留 | 既有測試綠 |
| B 本地 sense＋薄方法卡強制載入 | **已交** | `references/local-sense.md`；`SKILL.md` §0／§2／§4 |
| C 雲端多源（≥2 active）＋增刪規則 | **已交** | `references/cloud-sources.md` |
| D 機械閘：缺證據門／GAP+高風險 → fail | **已交** | `scripts/sense_gate.py` + `test_sense_gate.py` |
| E 紅線：無 cookbook／PoC／逐步利用進 skill | **守住** | 卡內容僅方法／門檻／死路／查法 |
| F session-load 可 mark 子目錄卡 | **已交** | `hunt_plan.py` 短名允許一層 `/` |

## 路徑一覽

```
huntspear/
  SKILL.md                          # 熱路徑＋切開條款
  CHANGELOG.md                      # 2026-09-26 條
  DELIVERABLE-2026-09-26.md         # 本清單
  references/
    local-sense.md
    cloud-sources.md
    sense-cards/
      http-observe-only.md
      evidence-gate.md
      dead-path-mark.md
      public-doc-cve-lookup.md
      local-sense-memory.md
    tradecraft-index.md             # 症狀表已掛
  scripts/
    sense_gate.py
    test_sense_gate.py
    hunt_plan.py                    # session-load 子目錄
```

Vault 人讀鏡像：可選；runtime 真源＝本樹。

## 刻意未做（非今晚主線）

- 不吞 CyberStrike／AGPL cookbook
- 不改 warboard production UI
- 未 `git push`（工作樹就緒，等指揮／Alfred 指示）

## Commit 草稿（未執行；等 Alfred／主人授權）

```
feat(huntspear): local sense gate + multi-cloud sources on hot path

- Add local-sense, cloud-sources, sense-cards (methodology only)
- Wire SKILL progressive disclosure + §4 technique/methodology split
- Add sense_gate.py with tests; allow session-load nested card names
- Map vault PB cards; sync method text; keep red line (no PoC/cookbook)
```

已拆獨立 repo：https://github.com/sinwei802/huntspear
