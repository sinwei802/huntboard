# State Bundle Schema v2 — 核心全載、證據按需

使用目錄：`./pentest-state/`。本文件自洽。

## Bundle 組成（五核心檔）

| 檔案 | 用途 |
|------|------|
| `session-index.json` | engagement scope、target、mode、bundle metadata |
| `asset-graph.md` | 資產、服務、身份、信任、reachability |
| `route-stack.md` | active／paused／closed 路線與假設 |
| `loot-tracker.md` | credential、token、key、ticket、pivot 等 |
| `evidence-index.json` | claim ↔ artifact 映射（不含 artifact 本文） |

`loot/**`、`payloads/**`、`tools/**` 等 artifact 不屬核心，啟動時不預載。

**可選 overlay**：`hunt-plan.md`（戰役計畫）。沒有不降級。brief 不倒正文，只印態勢列、觀察缺口、活躍賭注的 expect／kill_if、已關賭注的 id。`--full` 才倒正文。欄位以 `scripts/hunt_plan.py` 為真源。只有 checkpoint 才寫入。缺檔時計畫只活在作業脈絡與 HANDOFF 態勢列。

## 恢復協定

```bash
python3 "$SKILL_ROOT/scripts/load_state_bundle.py" ./pentest-state
python3 "$SKILL_ROOT/scripts/load_state_bundle.py" --full ./pentest-state
```

預設 stdout 是摘要（status、session last_stop、各核心檔位元組、hunt-plan 態勢列與缺口）。`--full` 才倒核心檔與 hunt-plan 正文。artifact 正文無論哪種模式都不預載。

`SKILL_ROOT` = 本回合載入的 `SKILL.md` 所在目錄（Claude：`$SKILL_DIR`）。不要寫死任何 harness 的安裝路徑。

| Exit | 意義 |
|------|------|
| 0 | 五檔完整且一致 |
| 1 | 降級（缺檔／格式／checkpoint 不一致），仍載入可用內容 |
| 2 | 無可用核心狀態，當新 session |

- 新訊息目標若不在已恢復 scope，不得自動合併；回報衝突並等待指示。
- 讀取狀態不形成任何目標互動授權。

## Artifact 存放規則（硬規則）

所有要保存的 artifact（掃描輸出、憑證、exploit 腳本、dump 等）**必須**放在 `./pentest-state/` 的子目錄下（通常 `./pentest-state/loot/`）。

- **禁止**把要保存的 artifact 放在 `pentest-state/` 外（如 `./.scan-tmp/`、`./scan/`、`/tmp`）。
- ephemeral 掃描的暫存目錄（如 `./.scan-tmp/`）只用於不需要進 evidence-index 的即時結果；一旦該結果需要被 evidence-index 引用，必須移入 `pentest-state/loot/` 再寫入 index。
- evidence-index 的 `artifacts[].path` 相對於 `pentest-state/` 解析，不得含 `..`，解析後須仍在 `pentest-state/` 內。
- port-scan-pipeline 的 engagement persist 也必須寫到 `pentest-state/loot/` 之下。

## Evidence 按需重讀

啟動只讀 `evidence-index.json`。僅在 active 假設／下一步直接引用、高衝擊 claim、即將使用 credential、freshness 過期、狀態衝突或使用者要求核對時，才依 index 開啟具名 path。

## Checkpoint

只有使用者明確要求「保存進度／checkpoint／同步 pentest-state」時才寫入。  
「確認／繼續／結束／done」不算保存。

戰鬥路徑：把本場事實寫成一份 JSON，跑：

```bash
python3 "$SKILL_ROOT/scripts/checkpoint_write.py" --facts <檔> ./pentest-state
```

腳本渲染五核心檔與可選 `hunt-plan.md`、對齊 metadata、驗證後才覆蓋；失敗則原檔不動。禁止手寫核心檔。禁止為對格式讀本檔或腳本源碼。欄位以 `checkpoint_write.py --print-schema` 為準。失敗一次：依 stderr 改 facts JSON 再跑一次。第二次仍失敗：停，把錯誤交指揮。

`load_state_bundle.py --stamp` 只對齊 metadata／補空骨架，不是戰鬥寫入器。

## Metadata

Markdown 核心檔第一行固定標題，第二行：

```markdown
<!-- state: {"schema_version":2,"checkpoint_id":"...","last_updated":"2026-...+08:00"} -->
```

JSON 核心檔 top-level 必須含 `schema_version`（整數 2）、`checkpoint_id`、`last_updated`（含時區的 ISO 8601）。

Loader 亦接受歷史標記名 `state` 變體，以讀取既有相容格式的檔案。

## Stable ID

| Prefix | 對象 |
|--------|------|
| A-* | Asset |
| R-* | Route |
| H-* | Hypothesis |
| L-* | Loot |
| E-* | Evidence |

ID 在同一 engagement 內唯一且穩定；關閉後不得重號給新對象。

## 最小表格要求（摘要）

- **asset-graph.md**：`# Asset Graph` + metadata + 含 ID 欄的表格（A-*）
- **route-stack.md**：`# Route Stack` + metadata + Route 表（R-*）+ 當前假設（H-*）+ Closed/Paused 表（含 scoped reopen-if）
- **loot-tracker.md**：`# Loot Tracker` + metadata + 材料表（L-*）
- **session-index.json**：targets、scope、mode（pentest|ctf）、last_stop
- **evidence-index.json**：entries[] 含 id、state_refs、claim、relation、confidence、freshness、availability、artifacts

詳細欄位與驗證邏輯由 `scripts/load_state_bundle.py` 執行。
