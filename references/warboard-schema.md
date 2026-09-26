# Warboard Schema Draft v0

## Status

**Status: draft**（v0）。Warboard 共用真源的 schema 草案；實作可能落後於本檔。  
**尚未**強制接入 hunting 熱路徑。欄位名英文 snake_case；語意說明繁中。


## 目的

把 huntboard 從「markdown 五核心 bundle」演化成**持久化、多 realm／多 host 的 CTF／滲透作戰台（warboard）**共用真源：

- SQLite 為共享真相（shared truth）
- 主控台以**可篩選的 host／service 表**（assets ⋈ surfaces）＋ **focus／pending-approval 條**為主視圖
- 互動是**活的 engagement graph**，不是階段精靈（stage wizard）
- HTB 式 ports→foothold→user→root 只是圖上的一條路徑，不是 schema

## 非目標（v0）

- 不實作 production UI／地圖視圖
- 不取代現行 hunting 熱路徑的 R1–R8／H1–H4 行為（本檔僅定義未來真源）
- 不要求指揮手改 SQL／Markdown
- 不把「階段」寫成必經流水線欄位

## 與既有 `./pentest-state/` 的關係（共存）

| 軌道 | 路徑慣例 | 角色 |
|------|----------|------|
| **現行** markdown bundle | `./pentest-state/` 五核心檔＋可選 `hunt-plan.md` | 仍為 hunting skill 執行時狀態；見 `state-schemas.md` |
| **新** warboard SQLite | `./pentest-state/warboard.sqlite`（相對 engagement cwd） | 未來共用真源；以本 draft schema 為契約，實作／console 驗證 |

- **禁止刪除**既有 `state-schemas.md` 與 markdown 寫入路徑，直到正式遷移完成。
- 兩軌並存期間：設計與 console 驗證讀本檔；戰鬥熱路徑仍走 markdown bundle。
- 遷移後：warboard 為唯一 shared truth；markdown 可降為匯出／唯讀快照（另議）。

---

## 實體詞彙表

| 實體 | 英文表名 | 意義 |
|------|----------|------|
| Engagement | `engagements` | 一場授權作業（一場 CTF／一次 pentest scope） |
| Realm | `realms` | 作業內的信任／網路域（如 HTB lab、內網 VLAN、雲專案） |
| Asset | `assets` | **Host**（機器／節點）；主表列的一列主體 |
| Surface | `surfaces` | 資產上暴露的服務／入口（port、URL、named pipe…） |
| Identity | `identities` | 已知主體（帳號、角色、機器帳號、匿名） |
| Loot | `loot` | 取得的材料（憑證、hash、檔、ticket…） |
| Edge | `edges` | 圖邊：資產／身份／面之間的關係或達成路徑 |
| Hypothesis | `hypotheses` | 可檢驗賭注／假設 |
| Goal | `goals` | 戰役目標（能力或狀態目標） |
| Focus | `focus` | 當前注意力＋**待決決策**（pending_decision_json）＋phase |
| Event | `events` | **僅附加**的事實／動作／決策日誌 |

---

## 列舉（務必對齊）

### `engagements.status`
| 值 | 意義 |
|----|------|
| `draft` | 已建尚未開打 |
| `active` | 進行中 |
| `paused` | 暫停 |
| `closed` | 結束（含成功／放棄） |

### `realms.kind`
| 值 | 意義 |
|----|------|
| `lab` | CTF／練習場 |
| `corp` | 企業／客戶內網 |
| `cloud` | 雲租戶／專案 |
| `segment` | 網段／VLAN／信任島 |
| `other` | 其他 |

### `assets.status`
| 值 | 意義 |
|----|------|
| `unknown` | 僅知存在／IP |
| `reachable` | 可達未深觀 |
| `mapped` | 面已大致標完 |
| `foothold` | 已有非特權執行／殼 |
| `user` | 使用者級控制 |
| `root` | 高權／系統級 |
| `oos` | 超出範圍 |

### `surfaces.status`
| 值 | 意義 |
|----|------|
| `unseen` | 推測或列埠但未碰 |
| `seen` | 已觀察（banner／回應） |
| `fingerprinted` | 產品／版本大致確認 |
| `interesting` | 值得跟進 |
| `oos` | 超出範圍或不打 |

### `identities.kind`
| 值 | 意義 |
|----|------|
| `user` | 自然人帳號 |
| `service` | 服務／機器帳號 |
| `role` | 角色／群組抽象 |
| `anonymous` | 匿名／未認證主體 |
| `other` | 其他 |

### `identities.privilege_band`
| 值 | 意義 |
|----|------|
| `none` | 無有效權 |
| `low` | 低權／guest |
| `user` | 一般使用者 |
| `admin` | 管理級 |
| `system` | SYSTEM／root 級 |
| `unknown` | 未知 |

### `loot.kind`
| 值 | 意義 |
|----|------|
| `credential` | 密碼／金鑰材料 |
| `hash` | hash／NTLM 等 |
| `token` | session／API token |
| `ticket` | Kerberos／類似票證 |
| `file` | 檔案／dump 片段 |
| `note` | 純文字線索 |
| `other` | 其他 |

### `loot.sensitivity`
| 值 | 意義 |
|----|------|
| `low` | 公開或低敏 |
| `medium` | 內部 |
| `high` | 可登入／可冒充 |
| `critical` | 高權或大範圍影響 |

### `hypotheses.status`
| 值 | 意義 |
|----|------|
| `open` | 未決 |
| `supported` | 證據支持 |
| `refuted` | 已否證 |
| `scoped_out` | 暫不追（可 reopen） |

### `goals.status`
| 值 | 意義 |
|----|------|
| `proposed` | 提出未接 |
| `active` | 進行中 |
| `achieved` | 達成 |
| `abandoned` | 放棄 |
| `blocked` | 卡住待解 |

### `focus.phase`（注意力相位，**不是** stage wizard）
| 值 | 意義 |
|----|------|
| `orient` | 對齊 scope／盤點 |
| `map` | 擴面／標面 |
| `probe` | 檢驗假設 |
| `exploit` | 利用／取得 |
| `persist` | 鞏固／橫移準備 |
| `decide` | 等待指揮決策 |
| `idle` | 無待決 |

### `edges.kind`
| 值 | 意義 |
|----|------|
| `hosts` | A 託管／含 B |
| `exposes` | asset→surface |
| `authenticates_as` | 以某 identity 作用 |
| `yields` | 路徑產出 loot／identity |
| `reaches` | 網路／信任可達 |
| `supports` | 證據支持假設 |
| `blocks` | 阻礙目標 |
| `derived_from` | 衍生自 |
| `other` | 其他 |

### `events.kind`
| 值 | 意義 |
|----|------|
| `observation` | 觀測寫入 |
| `action` | Agent 執行動作摘要 |
| `decision` | 指揮決策落盤 |
| `proposal` | 提案寫入 focus |
| `state_change` | 列狀態變更 |
| `note` | 人工／系統註記 |
| `error` | 錯誤／失敗類 |

---

## 各表定義

慣例：

- 主鍵皆 `id TEXT PRIMARY KEY`（穩定字串，如 `E-1`、`A-web01`）
- 時間欄 `TEXT`，ISO 8601 含時區（建議 `+08:00`）
- `created_at` NOT NULL；有更新語意者另備 `updated_at`
- FK 指向父列；刪除策略由應用層約束（v0 不做 CASCADE 業務刪）

### 1. `engagements`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| name | TEXT | NO | |
| status | TEXT | NO | enum `engagements.status` |
| mode | TEXT | NO | `ctf` \| `pentest` \| `other` |
| scope_notes | TEXT | YES | |
| created_at | TEXT | NO | |
| updated_at | TEXT | NO | |

**索引**：`(status)`  
**不變式**：同一時刻一個 cwd 對應一個主 engagement 列（慣例）；`status` 必須為列舉值。

### 2. `realms`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| name | TEXT | NO | |
| kind | TEXT | NO | enum `realms.kind` |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |

**索引**：`(engagement_id)`, `(engagement_id, kind)`  
**不變式**：必屬唯一 engagement。

### 3. `assets`（Host）

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| realm_id | TEXT | NO | → `realms.id` |
| hostname | TEXT | YES | |
| address | TEXT | YES | IP／名稱至少一 |
| status | TEXT | NO | enum `assets.status` |
| os_guess | TEXT | YES | |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |
| updated_at | TEXT | NO | |

**索引**：`(engagement_id)`, `(realm_id)`, `(engagement_id, status)`, `(address)`  
**不變式**：`hostname` 與 `address` 不可同時為 NULL；`realm_id` 必須同 engagement。

### 4. `surfaces`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| asset_id | TEXT | NO | → `assets.id` |
| engagement_id | TEXT | NO | → `engagements.id`（冗餘便於查） |
| kind | TEXT | NO | 如 `tcp`/`udp`/`http`/`https`/`named_pipe` |
| port | INTEGER | YES | |
| path_or_name | TEXT | YES | URL path／share／pipe 名 |
| banner_or_product | TEXT | YES | |
| status | TEXT | NO | enum `surfaces.status` |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |
| updated_at | TEXT | NO | |

**索引**：`(asset_id)`, `(engagement_id, status)`, `(engagement_id, port)`  
**不變式**：同一 asset 上 `(kind, port, path_or_name)` 邏輯唯一（應用層）；status 為列舉。

### 5. `identities`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| realm_id | TEXT | YES | → `realms.id` |
| label | TEXT | NO | 顯示名 |
| kind | TEXT | NO | enum `identities.kind` |
| privilege_band | TEXT | NO | enum `identities.privilege_band` |
| asset_id | TEXT | YES | → `assets.id`（本地帳時） |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |

**索引**：`(engagement_id)`, `(realm_id)`, `(kind)`  
**不變式**：`privilege_band`／`kind` 為列舉。

### 6. `loot`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| kind | TEXT | NO | enum `loot.kind` |
| sensitivity | TEXT | NO | enum `loot.sensitivity` |
| label | TEXT | NO | |
| storage_ref | TEXT | YES | 相對 `./pentest-state/` 路徑或 blob key |
| source_asset_id | TEXT | YES | → `assets.id` |
| source_surface_id | TEXT | YES | → `surfaces.id` |
| identity_id | TEXT | YES | → `identities.id` |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |

**索引**：`(engagement_id, kind)`, `(sensitivity)`, `(source_asset_id)`  
**不變式**：高敏材料禁止把秘密原文寫進 `notes`（只存 ref）；kind／sensitivity 為列舉。

### 7. `edges`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| kind | TEXT | NO | enum `edges.kind` |
| src_type | TEXT | NO | 實體類名：asset\|surface\|identity\|loot\|hypothesis\|goal |
| src_id | TEXT | NO | |
| dst_type | TEXT | NO | 同上 |
| dst_id | TEXT | NO | |
| label | TEXT | YES | |
| created_at | TEXT | NO | |

**索引**：`(engagement_id, kind)`, `(src_type, src_id)`, `(dst_type, dst_id)`  
**不變式**：src／dst 必須指向同 engagement 內已知列（應用層）；禁止自環除非 `kind=other` 且註明。

### 8. `hypotheses`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| claim | TEXT | NO | |
| status | TEXT | NO | enum `hypotheses.status` |
| related_asset_id | TEXT | YES | → `assets.id` |
| related_surface_id | TEXT | YES | → `surfaces.id` |
| expect | TEXT | YES | |
| kill_if | TEXT | YES | |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |
| updated_at | TEXT | NO | |

**索引**：`(engagement_id, status)`  
**不變式**：status 為列舉；`scoped_out` 應在 notes 或另表記 reopen-if（v0 用 notes）。

### 9. `goals`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| title | TEXT | NO | |
| status | TEXT | NO | enum `goals.status` |
| success_criteria | TEXT | YES | |
| notes | TEXT | YES | |
| created_at | TEXT | NO | |
| updated_at | TEXT | NO | |

**索引**：`(engagement_id, status)`  
**不變式**：同一 engagement 可多 goal；建議最多一個 `active`（應用層軟約束）。

### 10. `focus`

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` UNIQUE |
| phase | TEXT | NO | enum `focus.phase` |
| summary | TEXT | YES | 條上短敘 |
| active_asset_id | TEXT | YES | → `assets.id` |
| active_goal_id | TEXT | YES | → `goals.id` |
| pending_decision_json | TEXT | YES | JSON，見下 |
| updated_at | TEXT | NO | |

**索引**：`UNIQUE(engagement_id)`  
**不變式**：每 engagement **恰好一列** focus；有未決提案時 `phase` 應為 `decide`；決策落盤後清或改寫 pending。

#### `pending_decision_json` 形狀

```json
{
  "options": [
    {
      "id": "opt-1",
      "label": "先打 web 那台的 80",
      "action_class": "fingerprint",
      "approval": "confirm_required",
      "rationale": "唯一 HTTP 面且 status=interesting"
    },
    {
      "id": "opt-2",
      "label": "對 ssh 做 banner／金鑰觀測",
      "action_class": "observe",
      "approval": "pre_authorized",
      "rationale": "低侵、對齊 map 相位"
    }
  ],
  "selected_option_id": null,
  "commander_utterance": null,
  "decided_at": null
}
```

- `options` 長度 **2..3**
- 每項必有：`id`, `label`, `action_class`, `approval`（`pre_authorized` \| `confirm_required`）, `rationale`
- `selected_option_id` 可 null；選定後必須是某個 `options[].id`
- `commander_utterance`：指揮原話（寬鬆自然語）
- `decided_at`：決策落盤時間；未決為 null

### 11. `events`（append-only）

| 欄位 | 型別 | Null | FK／約束 |
|------|------|------|----------|
| id | TEXT | NO | PK |
| engagement_id | TEXT | NO | → `engagements.id` |
| kind | TEXT | NO | enum `events.kind` |
| body_json | TEXT | NO | 結構化摘要 |
| actor | TEXT | NO | `agent` \| `commander` \| `system` |
| related_focus_id | TEXT | YES | → `focus.id` |
| created_at | TEXT | NO | |

**索引**：`(engagement_id, created_at)`, `(engagement_id, kind)`  
**不變式**：

- **禁止 UPDATE／DELETE**（僅 INSERT）
- 決策類事件必須在後續 action 之前寫入
- `body_json` 為合法 JSON 物件字串

---

## 主控台查詢草圖（assets ⋈ surfaces）

```sql
SELECT
  r.name AS realm,
  a.id AS asset_id,
  COALESCE(a.hostname, a.address) AS host,
  a.status AS asset_status,
  s.id AS surface_id,
  s.kind AS surface_kind,
  s.port,
  s.path_or_name,
  s.banner_or_product,
  s.status AS surface_status
FROM assets a
JOIN realms r ON r.id = a.realm_id
LEFT JOIN surfaces s ON s.asset_id = a.id
WHERE a.engagement_id = :engagement_id
  AND (:realm_id IS NULL OR a.realm_id = :realm_id)
  AND (:asset_status IS NULL OR a.status = :asset_status)
  AND (:surface_status IS NULL OR s.status = :surface_status)
ORDER BY r.name, host, s.port NULLS LAST, s.kind;
```

Focus 條另查：

```sql
SELECT phase, summary, pending_decision_json, active_asset_id, active_goal_id
FROM focus
WHERE engagement_id = :engagement_id;
```

---

## Status notes

本檔為 **draft v0**：schema／列舉供實作與實用後修改；驗收以對齊本 schema 的真實 console／SQLite 為準，不以紙上 mock 腳本為準。  
**尚未**接入 hunting skill 執行迴圈；熱路徑仍以 `state-schemas.md`／markdown bundle 為準。  
契約行為見同目錄 `interaction-truth-contract.md`。
