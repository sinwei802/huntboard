# Interaction / Truth Contract Draft v0

## Status

**Status: draft**（v0）。與 `warboard-schema.md` 配套的 warboard 共用真源互動契約；實作可能落後於本檔。  
尚未接入 production hunting 熱路徑。驗收以對齊本契約的真實 console 為準。

## 角色

| 角色 | 誰 | 職責 |
|------|----|------|
| **Commander** | 人類指揮 | 給 scope、用**寬鬆自然語**選方向／批准；不手改 DB／Markdown |
| **Agent** | huntspear skill | 在已授權方向內執行；把結構化結果寫入 shared truth；提出 2–3 個正交下一刀；停等 |

實作／UX 驗證時，指揮以自然語決策；Agent 負責寫回 shared truth。

## Shared truth

- **唯一作戰台真源（本契約）**：SQLite  
  路徑慣例（相對 engagement cwd）：

  ```text
  ./pentest-state/warboard.sqlite
  ```

- Schema：`references/warboard-schema.md`＋`scripts/warboard_schema.sql`
- 現行 markdown 五核心 bundle（`state-schemas.md`）在遷移完成前**並存**；本契約談的是 warboard 軌道。
- 指揮**禁止**手編輯 Markdown／SQL 來「改真相」。語言決策一律由 Agent **寫回** focus／events。

## 回合迴圈（Turn loop）

```text
1. Agent 執行「已授權方向」內的動作
2. Agent 寫入結構化列（assets／surfaces／identities／loot／edges／hypotheses／goals…）
3. Agent APPEND events（observation／action／state_change…）
4. Agent 更新 focus：phase、summary、pending_decision_json（2–3 正交選項）
5. Agent APPEND event kind=proposal → STOP，等待指揮
6. Commander 以寬鬆自然語回覆（例：「先打那台 web」「可以，走選項2」）
7. Agent 解讀 → 必須先把決策寫入 focus.pending_decision_json
   （selected_option_id／commander_utterance／decided_at）並 APPEND event kind=decision
8. 然後才依選定 option 的 action_class／approval 邊界執行下一方向
9. 回到 1
```

**正確性優於polish**：永遠開著的 ops console；表＋focus 條即可。

## 硬規則

1. **無 stage wizard UI**：相位只是 focus.phase 注意力標籤，不是必經關卡。
2. **指揮不手改** Markdown／SQL；一切決策經自然語 → Agent 寫回。
3. **語言決策必寫回** shared truth（focus＋events），不可只活在對話裡。
4. **events 僅附加**：執行層不得 UPDATE／DELETE `events`。
5. **Agent 不得發明授權**：只能 consummate 當前 pending decision 的解析結果；不可把「新發現」當新授權（對齊 R1／R2 精神）。
6. **R1 式方向邊界仍適用（概念上）**：一則指揮訊息＝一個已授權方向；決策邊界停；動作類升級需新決策。
7. **提案必須 2–3 個且正交**（不同面／不同賭注／不同風險軸），不得三個同義覆述。
8. **先決策落盤，後行動**：未寫 `decision` event 與 selected_option_id 前，禁止開下一方向的 action event。

## Focus 條 vs Host／Service 表

| 區塊 | 內容 |
|------|------|
| **Host／service 表** | `assets ⋈ surfaces`（可加 realm／status 篩選）；顯示 host、asset.status、port／kind、surface.status、banner |
| **Focus／pending 條** | focus.phase、summary、active asset／goal、**pending_decision_json 的選項列表與批准態**；選定後顯示已選 id 與指揮原話 |

地圖視圖：**延後**，不在本契約範圍。

## Agent 寫入期望

- 掃描／指紋結果 → `surfaces`（＋必要時 `assets`）＋ `events.observation`
- 假設變化 → `hypotheses`＋`events.state_change`
- 取得材料 → `loot`（秘密進 storage_ref，不進 notes 明文）＋可選 `edges.yields`
- 每輪結束 → 更新 `focus.pending_decision_json`＋`events.proposal`
- 解讀指揮語 → 更新 focus 決策欄位＋`events.decision`，**然後**才 `events.action`

## 驗證期望（實作／UX）

以真實作戰台（SQLite 共用真源＋指揮口語寫回）與 console／UX 驗證為準，至少涵蓋：

1. 自 `warboard_schema.sql` 建庫並種多 realm／多 host 種子
2. Agent：寫入 scan→surfaces／events；寫入 2–3 options 到 focus；停止等待
3. Commander：寬鬆 NL（如「先打那台 web」「可以，走選項2」）映射到選項並持久化
4. 不變式：
   - events 無 UPDATE／DELETE
   - 決策寫入發生在下一 action 之前
   - 提案數量：非 `idle` 時 ∈ {2, 3}；`phase=idle` 收束／待命時 ∈ {0, 2, 3}（允許空 options，不必發明假選項）
   - 主 join 查詢有列
   - 無效 option id 被拒絕
   - 每 engagement 僅一 focus

## Status notes

本契約為 OSS 維護草案。實作對齊 schema 並經真實 console 驗證後，再決定是否把 warboard 接入 session 啟動與 HANDOFF 寫回。現階段 hunting 熱路徑仍遵守 `SKILL.md` 與 markdown `./pentest-state/`。
