## 2026-09-28 — 週一雙軌維護（vault 對齊＋雲端增源）

- vault `資安/HuntSpear 薄 playbook` 與 sense-cards 漂移收斂（skill 為戰鬥真源）：提權分流第三態、禁 PoC 交叉段、主人尺／Web 階梯／复盤用語去內部場次標。
- `dead-path-mark`：補齊 `doctrine-incompatible`／`platform-deny`／session／advisory 類標記（方法層，無利用步驟）。
- `public-doc-cve-lookup`：MQTT 指紋時指向 `src-mqtt-oasis`。
- `cloud-sources`：健康檢查全過；新增 active `src-mqtt-oasis`（OASIS MQTT／Mosquitto 官方文件；禁 exploit）。
- 索引補掛站穩後地圖／提權證據門。無 payload／PoC。

- 2026-09-26：`doctrine-compatible-privesc` 補第三態 `DEAD:platform-deny`（有 misconfig 面但程序／平台拒批之抽象形）。
## 2026-09-26 — 成敗都迭代＋提權分流卡

- 新卡：`owner-root-flag-bar`、`doctrine-compatible-privesc`、`post-engagement-retro`
- 強化：`priv-esc-evidence-gate` 交叉禁 PoC 分流
- 觸發：主人尺只認 root flag；相容提權成功形 vs 需 PoC 不相容卡死
- 禁止：payload／PoC／自報 PASS

## 2026-09-26 — wire Web method cards into sense_gate

- `KNOWN_CARDS` 補上 `web-app-evidence-ladder`、`challenge-board-handoff`、`session-break-rebuild`（卡與 local-sense／vault-map 已有；閘門名單漏掛）
- `test_sense_gate.py` 增三張卡 PASS 用例
- 無 payload

## 2026-09-26 — Web 挑戰盤交班＋防卡死 observe

**根因（方法層）**：`http-observe-only` 易讓副駕駛停在指紋；挑戰盤入 HAVE 後缺少「必須交可稽核下一階」卡；指揮若過早收斂利用授權，訓練場最低達標（admin／≥1 challenge）永遠碰不到。

**改動**（皆無 payload／PoC）：
- 新增 `sense-cards/challenge-board-handoff.md`（交班句式）
- 強化 `web-app-evidence-ladder.md`（強制交班）、`http-observe-only.md`（何時離開只觀察）
- `local-sense.md` 掛卡＋允許具名可稽核 CONFIRM HANDOFF
- `SKILL.md` §0 熱路徑一句；`tradecraft-index`／`sense-vault-map` 同步
- 先前已有：`session-break-rebuild.md`

**驗收（方法層）**：公開 observe 齊後 HANDOFF 須見挑戰向／管理面／重建之一；不開解法／封條正文。

## 2026-09-26 — Web 階梯＋session 斷裂卡

- 新增 `sense-cards/web-app-evidence-ladder.md`、`sense-cards/session-break-rebuild.md`（方法／證據門；**無** payload）
- 觸發：Web 訓練場觀察收場未達最低達標；Linux misconfig 路徑已驗證 sense→授權升級
- `tradecraft-index.md` 已掛症狀列

# huntspear CHANGELOG

## 2026-09-26 — staged Hard×4 sense cards (post-foothold / priv-esc gate)

- Add thin method cards `post-foothold-map` / `priv-esc-evidence-gate` (Chinese; 何時用／要驗證什麼／證據長什麼樣／死路／去哪查). **No** payload／PoC／exploit steps.
- Wire into `sense_gate.py` `KNOWN_CARDS`, `local-sense.md`, `sense-vault-map.md`, `test_sense_gate.py`, vault `資安/HuntSpear 薄 playbook/`.
- Acceptance bar moves to staged `00→05` root/DA rehearsal (methodology); prior orient/map-only PASS void.


滾動更新，不寫版本號（rolling skill 慣例）。最新在上。

## 2026-09-26 — 隔夜可用：載入路徑＋分階驗收指標

本地 sense 已焊；本則補「起用」與驗收指標說明。薄 playbook 為加分（vault 鏡像對照），非硬掛載。

### 新增／交付
- `USER.md`：載入說明、warboard console／sqlite 註記、events-fold 凍結債
- 分階 root／DA 驗收指標（方法論；**無**解法／writeup／exploit 步驟；題面產物不進本 repo）
- 安裝：以本 `huntspear/` 目錄為 `$SKILL_ROOT`（各 harness symlink 同一樹）

### 未動
- 不改 events-fold UI；不改 huntseeker／不併攻擊 cookbook

## 2026-09-26 — 本地 sense＋多雲端源焊進熱路徑

交件目標：補「會搜沒 sense」；紅線不變（無攻擊 cookbook／PoC 進 skill）。

### 新增
- `references/sense-vault-map.md`：sense-cards ↔ vault PB 對照與回寫規則
- `references/local-sense.md`：方法／證據門強制程序；與「禁止 Route 手法 playbook」切開
- `references/cloud-sources.md`：active／watch 多源登錄與增刪規則
- `references/sense-cards/`：五張薄方法卡（http-observe-only、evidence-gate、dead-path-mark、public-doc-cve-lookup、local-sense-memory）
- `scripts/sense_gate.py`：提案 JSON 機械閘（缺欄／模糊證據／GAP+高風險 → fail）
- `scripts/test_sense_gate.py`

### 修改
- `references/interaction-truth-contract.md`：`phase=idle` 允許 0 個 options（不發明假選項）
- `references/tradecraft-index.md`：症狀表加 local-sense／cloud-sources
- vault `HuntSpear 薄 playbook.md`：標 runtime 真源對齊（非第二份手法庫）
- `SKILL.md` §0：提案前載 `local-sense`／必要時 sense-card；DESIGN 載 `cloud-sources`；可跑 sense_gate
- `SKILL.md` §2：本地 sense 先於下一刀
- `SKILL.md` §4：手法 playbook 禁令保留；方法薄層允許並強制對卡
- `hunt_plan.py`：`session-load` 短名允許一層子目錄（`sense-cards/<id>`）

### 未動
- R1–R8／H1–H4 行為閘
- warboard production UI
- CyberStrike cookbook 不吞入

## 2026-09-23 — 移除 warboard mock 腳本

移除僅供紙上雙角色演練的 mock 腳本；schema、契約文件與 SQL DDL 保留為維護草案。

### 刪
- `scripts/warboard_mock_drill.py`
- `scripts/test_warboard_mock_drill.py`

### 保留
- `scripts/warboard_schema.sql`
- `references/warboard-schema.md`
- `references/interaction-truth-contract.md`

## 2026-09-23 — warboard schema／互動契約 draft v0

作戰台朝 SQLite 共用真源演化：表優先主控台、活 engagement graph。既有 markdown `state-schemas` 並存，不刪。

### 新增
- `references/warboard-schema.md`：11 表 draft v0（engagements…events）、列舉、focus.pending_decision_json、主 join 草圖。
- `references/interaction-truth-contract.md`：Commander／Agent 回合迴圈、硬規則、focus 條 vs host／service 表、驗證期望。
- `scripts/warboard_schema.sql`：對齊 draft 的 SQLite DDL。

### 修改
- `SKILL.md`：description 點出 warboard／ops console；§0 Progressive Disclosure 加 warboard 兩份參考（非戰鬥熱路徑）。

### 未動
- 其他 skill 目錄未改。
- 既有 `state-schemas.md`／markdown pentest-state 寫入路徑（並存）。
- production UI。

## 2026-09-23 — 已讀名單用腳本記；brief 不倒 hunt-plan 正文

指揮授權：保持狩獵能力，把 token 花在歷史重播上的部分降下來。先做兩刀。不把 R／H 搬出 `SKILL.md`。不寫「請省 token」。

### 修改
- `hunt_plan.py opening` 第二行印 `loaded=`。`session-load mark／reset` 把本對話已讀的 reference 短名記在本機 cache，用 session id 分開；檔案雜湊變了印 `stale=`。沒有 session id 則 `session=absent`，不寫檔。`/compact` 或 `/new` 的下一則先 `reset`。
- `load_state_bundle.py` brief：`hunt-plan.md` 只印態勢列、觀察缺口、活躍賭注的 expect／kill_if、已關賭注 id。`--full` 才倒正文。`last_observed` 這類長欄不進 brief。

### 刪／降
- brief 把整份 `hunt-plan.md` 用 `BEGIN OVERLAY` 倒進 stdout。
- 已讀名單不進 `./pentest-state/`，也不復活戰鬥路徑的 `--stamp`。

### 候選
- `2026-09-23-session-load-and-brief-plan` → promoted（指揮明示；中度，未動 R1–R8）。

## 2026-09-22 — 對指揮用台灣口語，禁翻譯腔骨架

指揮授權：Grok 對指揮的中文容易變成翻譯腔。禁句型，不禁單字。只綁講給指揮聽的正文。

### 修改
- `SKILL.md` §2：熱路徑加一句。台灣口語繁中；工具名、CVE、路徑、指令保持英文。禁止翻譯腔骨架與空動詞加名詞化。單字本身不禁。細節指回 `output-contract.md` §1.1。
- `output-contract.md` §1.1：補骨架清單、空動詞搭配、比喻詞、台灣用詞、只約束正文，以及一組 SMB 對照。

### 刪／降
- 沒有。欄位名、授權標籤、code fence、狀態檔的寫法不動。

## 2026-09-21 — 指揮 cons：已排序選項；checkpoint 一次寫入

指揮授權：Phantom 檢討。A1 交回改 2–3 條已排序選項（行為／預期／風險／停），「繼續」只確認建議。C1 保存進度改跑 `checkpoint_write.py`。Jev 本則不動。

### 修改
- HANDOFF：2–3 條選項，每條做什麼／預期／風險／停／為什麼現在；標建議。短詞只確認選項 1。禁止是非題，禁止缺口選單。checkpoint 回合只交態勢。
- R3／R7：短詞綁建議那條；建議選項缺標籤＝未完成。
- `scripts/checkpoint_write.py`：一份 facts JSON → 合法五核心檔 + hunt-plan、驗證後才覆蓋。
- §3 戰鬥路徑只跑該腳本；失敗一次改 JSON 再跑，第二次停。禁止手寫核心檔、禁止為對格式讀 schema。

### 刪／降
- 「回打／繼續」當唯一 CTA。
- 戰鬥路徑「手寫正文再 `load_state_bundle.py --stamp`」；「stamp 失敗才讀 schema」。
- memory「單一下一探 approve/reject」。

### 候選
- `2026-09-21-commander-briefing-options` → promoted（指揮點 A1；中度，R3／R7 只澄清短詞綁哪一條）
- `2026-09-21-checkpoint-write-once` → promoted（指揮點 C1；中度；n=2：Management + Phantom）
- `2026-09-16-checkpoint-stamp` → superseded

## 2026-09-16 — 新觀看者剩餘觀察；變體矩陣；loot 便宜探；checkpoint stamp

指揮授權：Management 事後討論，保持心法、不做 playbook。同一類失敗在開局以外的相位又發生：新身份沿第一份檔深挖、HTTP 矩陣做對但 argv 變體拆成多則確認、未用密文不進排序、保存進度卡在 schema。

### 修改
- H1：新觀看者（新 identity／command execution）進 HAVE → 資產面未標完前只准具名剩餘觀察 batch。詳 `hunt-loop.md` §2.4。11.5a 的下一方向預設走這份 batch，不是第一份檔的利用。
- §4.1：同一 expect／kill_if 的變體是一個方向。argv／旗標／路徑／mode 與 HTTP 通道同一類；HTTP 專名降為 illustration。
- 「最便宜」把未使用秘密 × 已點名身份／登入口算進去；HAVE 裡受約束執行者時 2–3 條裡必須有一條測剩餘參數能否蓋掉寫死的限制。
- 解讀已拉回材料的工具預設打手側。
- checkpoint：先寫事實，再 `load_state_bundle.py --stamp`。禁止為對格式讀 schema。

### 刪／降
- 「新 identity 是新資產面」空宣言（改成 H1 if-then）。
- §4.1 把 query／Cookie／Header 當閘的讀法；`pearcmd` 示例。
- 保存進度先讀 `state-schemas.md` 的戰鬥路徑。

### 候選
- `2026-09-16-viewer-remainder-batch` → promoted
- `2026-09-16-variant-matrix-not-http` → promoted
- `2026-09-16-loot-constraint-attacker-side` → promoted
- `2026-09-16-checkpoint-stamp` → promoted

## 2026-09-14 — 查庫不是開局儀式；腳本搜索引，模型不進 vault

指揮授權：依設計分析改 token 路徑。查 Obsidian 紙面上不貴，貴的是掛在每次啟動、組 `evidence-db` skill、跟著 wikilink 走進舊案。

### 修改
- `SKILL.md` §3：從「開局查證據資料庫」改成「本場第一次見到可索引 IOC 才跑 `ioc_lookup.py`」。無 IOC 或 CTF／HTB／THM／flag → 0 次讀 vault。
- 戰鬥中禁止 `read_file` vault 與 `evidence-db` SKILL.md。腳本搜索引，最多帶 1 個實體摘要（不含備註／案件筆記）。
- §0 開局三步明示不含查庫。§8 CTF 禁止跑 lookup。§10 收尾才載 `evidence-db` 寫庫。
- `scripts/ioc_lookup.py`：fixed-string 查總索引；路徑從 `evidence-db` 表／`OBSIDIAN_VAULT` 解析，huntspear 不硬寫 vault 路徑。

### 刪／降
- 開局必查 evidence-db 的儀式。
- 戰鬥中組 `evidence-db` skill 當查詢流程。
- 「命中再 `read_file` 1 個實體頁」（改由腳本帶摘要）。

### 候選
- `2026-09-14-ioc-lookup-not-opening` → promoted（指揮明示改載入閘；中度，未動 R1–R8）。

## 2026-09-10 — 實驗要有資訊量；迭代放能看見錯誤的地方

指揮授權：09-07 逐洞補丁（註解家族／同一畫面）與「打之前每格先答」那版結構稿都不照套。改成未來還用得上的兩條。

### 修改
- `SKILL.md` §2 外部材料：周圍環境也是環境維度；文章 payload 是假設來源。刪 ORDER BY／註解符。
- `SKILL.md` §2 偵查矩陣：分不開＝未決，不得寫已測／已否證／已窮盡。刪註解家族 gate。
- `SKILL.md` §2 新增「錯誤可讀處迭代」：片段已能跑且錯誤可讀 → 家族在那裡展開，目標只收倖存者。沒有現成環境不要停下來搭實驗室。本地命中≠目標命中。
- `hunt-loop.md` §4.1：第 3 項資訊量（允許少量探測發現塌縮，禁止把塌縮上的家族掃完當矩陣）；第 4 項周圍環境是獨立軸、符號家族 illustration；第 5 項錯誤可讀處迭代。
- §5 `kill_if` 塌縮 → `unknown_primitive` 不動（打完怎麼標；§4.1 管打的時候有沒有資訊）。

### 刪／降
- 「矩陣必須含註解／終結符家族」（gate）→ illustration。
- Claim／§9「同一畫面不得關注」→ 併進「分不開＝未決」。
- 09-07 apply 腳本改為拒絕執行，避免覆寫本版。

### 候選
- `2026-09-10-experiment-needs-signal` → promoted（中度；指揮明示不要照套 09-07 稿，改這條）。
- `2026-09-07-reconstruct-sql-suffix-before-kill`／`2026-09-07-undecidable-experiment-local-first` → superseded。

## 2026-08-28 — 指揮點名的 MCP／工具卡在允許提示時停等

指揮授權：Burp MCP 要人按允許時，不得改走 Proxy／curl 當等價通道。

### 修改
- `SKILL.md` §1：指揮點名的工具／MCP 卡在允許 → `[USER]` 停等。
- `execution-contract.md` §6：能力在人含 MCP 允許提示；禁止改走未點名通道。

### 刪／降
- 「通道卡住就換皮繼續」當合法下一探。

## 2026-08-28 — 本機 vantage（hosts）交給指揮，禁止單幹繞過

指揮授權：掃到 `gavel.htb` 這種已宣告名字時，要請指揮加 `/etc/hosts`，不要用 Host 標頭自己繼續打。

### 修改
- `SKILL.md` §1：本機 vantage 缺口是「能力在人」；已宣告名字本機解析不到 → `[USER]` 加 hosts。
- `htb-preflight.md` §2：從「建議補」改成必須把加列命令交給指揮。
- `hunt-loop.md` §2.1／`port-scan-pipeline.md` §2.2：掃完若有未解析主名，下一步是 USER hosts，剩餘觀察寫在加完之後。
- `execution-contract.md` §6、`output-contract.md` §1.3：vantage 進「能力在人」；不得把 hosts 命令改寫成 Host 標頭替代方案。

### 刪／降
- 「再建議補 hosts」（可選，模型就跳過）。
- 把只打 IP／改 Host 標頭當成「就不必請指揮加 hosts」的合法下一探。

### 候選
- `2026-08-28-hosts-is-user-collab` → promoted（指揮明示改互動；一般，未動 R1–R8）。

## 2026-08-26 — 採納 Claude 契約審查（R2 收緊使用／研究）

指揮授權：採納 Fable 審查的去重與可數化；R2 不用它的原句。

### 修改
- 「不等 Stall」只留 H2；frontmatter／開頭／§6.1 改指回。
- Stall 觸發改成連續 3 個 STEP 的 outcome 皆非 `fact_gained`／`new_surface`。
- 升級只當 CONFIRM 選項；H4 未關時不得取代 `next_probe`。
- R2：本則新秘密禁止同回合**使用**；已點名動作類可同回合搜怎麼做。
- 11.5a 加「換方向、不是收工」。
- 指揮態勢列只印 Goal／下一探；Phase 留在 overlay。

### 刪／降
- 四份「不等 Stall」複本。
- §9 與 §7 重複的 curl 禁令。
- 不採納「新拿到的只是參數」（會放寬新 cred 使用）。

### 候選
- `2026-08-26-claude-review-adopt` → promoted。

## 2026-08-26 — 指揮要判斷與介入，不看內部運作

指揮授權：品質、重要決策介入、正確判斷並討論。不在意內部運作。地板 GLM 5.2，不為弱模型留複本。

### 修改
- 戰鬥熱路徑不再載 `thinking-loop.md`。十二步只留給改 skill／除錯。
- HANDOFF 前對 R／H／§7，刪 16 條自檢默想。
- 搜尋預算數字只留 SKILL §6.1。
- §1 只留指揮面：人話、STEP 開關、開局口語、兩種交回味道、approval。R 不再複誦。
- Stall 在 main 收成「先問觀察／未測注，再提案一個 CONFIRM 否證」。

### 刪／降
- 「展開見 thinking-loop.md」。
- output-contract 十六條自檢。
- search-mindset／tactical-search 重抄的 3／5 query。
- §1 裡與 R1／R2／R3 重複的句子。

### 候選
- `2026-08-26-commander-not-internals` → promoted（指揮明示；中度，未動 R1–R8 語義）。

## 2026-08-26 — 狀態摘要載入；Source-first 限本場；砍 SKILL 複本

指揮授權：先改 token 浪費與邏輯衝突。三個真源在打架：loader 倒全文、Source-first 沒劃本場、SKILL 把紅線再抄一遍。

### 修改
- `load_state_bundle.py` 預設 brief（status、session last_stop、檔案大小、hunt-plan overlay）。`--full` 才倒核心檔正文。artifact 仍不預載。
- Source-first = 本 engagement 已取回材料。舊案／整個磁碟不是「已在手」。大檔先 grep／摘要。
- SKILL §1.2 收成兩行；§9 只留紅線沒寫的；刪 §11 檔名菜單。

### 刪／降
- 「讀完目前可及的來源」（無邊界）。
- 與 execution-contract 重複的 approval 表。
- §9 裡 R1–R8／H1–H4／§2 的否定複本。
- always-loaded 的 references 清單（路由在 §0）。

### 候選
- `2026-08-26-brief-state-source-scope` → promoted（指揮明示改進；中度，未動 R1–R8）。

## 2026-08-25 — Session-once 載入；材料攝入有上限

指揮授權：Grok 開局把半個套件反覆讀進 35 萬窗。契約層問題是「每批 ACT 再載」，不是少寫一句省 token。

### 修改
- 載入閘改 session-once：已注入的 `SKILL.md` 禁止再讀；腳本只執行不讀源碼；同一相對路徑本場已讀過不重讀。
- `execution-contract.md`：每 session 最多 1 次。開局觀察不必讀。重讀條件＝動作類升級或高風險 CONFIRM。
- 開局 evidence-db：只查本場已見 IOC 的索引，命中最多 1 個實體頁。禁止開局讀舊案 writeup／loot／源碼樹。
- 截圖：存檔＋HANDOFF 給路徑。禁止預設把圖灌進模型。相位邊界建議 `/compact` 或 `/new`。
- 本場只認載入的 `SKILL_ROOT`，禁止再讀另一個 harness 的同套件路徑。

### 刪／降
- 「ACT 前若本輪尚未讀過本文件，必須先讀」。
- 「即將 ACT／可執行命令／高風險確認」必讀 execution-contract。
- 「HANDOFF 必須內嵌圖／給指揮看圖」。

### 候選
- `2026-08-25-session-once-load` → promoted（指揮明示改契約；中度，未動 R1–R8）。

## 2026-08-25 — 關手法要回 Goal 換軸，禁止同產品換洞硬鑽

指揮授權：攻擊線太鑽牛角尖。技能有一部分責任：Goal 寫成產品洞、正交被讀成姊妹 CVE、bet_killed 自動 next-bet。

### 修改
- Goal 必須是能力語言。正交＝不同操作軸／信任邊界；同產品姊妹洞、同手法換通道不算。
- `bet_killed` 後若下一注只是換皮 → 回 DESIGN 或提出升級，不得再寫同產品檢測腳本當唯一下一探。
- `hypothesis-engine.md`／`hunt-loop.md` §3／§5／`SKILL.md` §2／§9。

### 刪／降
- 「有下一注就 next-bet」把同一口井裡的下一號 CVE 當成正交。

## 2026-08-25 — 一條賭注的偵查用腳本一次跑完

指揮授權：同一 primitive 的通道／編碼／對照是一個方向的偵查，不要現場試錯、每格請「繼續」。要想遠一點（含工具摺路徑假陽性），善用腳本。

### 修改
- `hunt-loop.md` §4.1：碰目標前寫矩陣＋對照，腳本一次跑，分類後才 HANDOFF。
- `SKILL.md` §2／§7／§9、`execution-contract.md` 並列探查、`thinking-loop.md`、`output-contract.md` 自檢第 11 條：指回 §4.1。

### 刪／降
- 把 query／Cookie／PATHINFO／編碼拆成多則請示的讀法（R1 本就禁止拆包；補上怎麼一次做完）。

## 2026-08-25 — 蒐集情報要截圖

指揮授權：觀察會渲染的網頁必須截圖，不能只 curl。writeup 嵌圖規則在 writeup skill，此處管何時截、存哪。

### 修改
- `hunt-loop.md` §2.3：未截圖不得把視覺材料標成已讀；存 `./pentest-state/loot/screenshots/`。
- `execution-contract.md` §6：未登入第一眼改為 ASSISTANT 截圖；互動登入仍 `[UI]`。
- `SKILL.md` §1／§7／§9、`output-contract.md`、`error-recovery.md`：curl 不算看過畫面。

### 刪／降
- 「未知 vhost 的第一眼預設 UI」（改成先截圖；要人操作才 UI）。
- 只描述「看起來是…」當視覺觀察。

## 2026-08-25 — 升級更能改 Goal 時必須提出，不得只在低權限打轉

指揮授權：副駕駛判斷需要更高權限，就該寫成可點名的下一步，不要替指揮把選項刪掉、在已批准的低權限裡空轉。

### 修改
- `SKILL.md` §2「最便宜」以達成 Goal 計；§7／§9：判斷升級更便宜時 HANDOFF 必須提出 CONFIRM 選項。
- `hunt-loop.md` DESIGN 排序：第一探若需動作類升級，不得改交同權限變體。
- `output-contract.md` 自檢第 16 條。

### 刪／降
- 「最便宜＝留在已批准動作類裡」的讀法。
- 不新增紅線編號、不寫 OS shell 食譜。提出仍≠執行（R1／R4）。

### 候選
- `2026-08-25-propose-privilege-upgrade` → promoted（指揮明示改契約；中度，未動 R1–R8）。

## 2026-08-19 — 指揮要跑的指令全部進 code fence

指揮授權：互動區塊裡，凡是要指揮執行的指令都必須包在 code fence。

### 修改
- `SKILL.md` §7：需要指揮跑的指令一律放 fence。
- `output-contract.md` 新增 §1.3 互動區塊 + 風險卡補 fence + 自檢第 15 條。
- `execution-contract.md` §8：全部進 fence；形狀指回 §1.3。

### 刪／降
- 把命令只寫在散文或行內 backtick 當交付。

### 候選
- `2026-08-19-user-commands-in-fence` → promoted。

## 2026-08-19 — 掃完表放進 markdown 程式碼區塊

指揮授權：表要能從對話一鍵複製貼進 Obsidian。渲染表複製不到 `|` 原文，必須用 code fence。

### 修改
- `SKILL.md` §7／`output-contract.md` §1.2／`port-scan-pipeline.md` §4：可列舉結果先放 `markdown` 程式碼區塊，再接三欄。標題形狀以指揮給的範本為準。
- `test_hunt_plan.py`：斷言必須用 code fence、禁止只渲染表。

### 刪／降
- 「禁止包進 code fence」。那條寫反了。
- 傳輸面回報以散文堆開埠當主格式。

### 候選
- `2026-08-19-scan-obsidian-tables` → promoted。

## 2026-08-18 — 對指揮回報：先人話、一句一事、能複述再交

指揮授權：執行者技術強於指揮；回報要貼近指揮能懂的密度，文字不能過精簡。

### 修改
- `SKILL.md`：輸出原則改為「對指揮說話要好懂」；§7 三欄同樣要求。
- `output-contract.md` 新增 §1.1（先人話再術語、一句一事、停在能複述、識別名不意譯、不唸閘門編號）+ 自檢第 13 條。
- `test_hunt_plan.py`：斷言 shipped 正文已去掉「輸出經濟且口語」，且 §1.1 在位。

### 刪／降
- 「輸出經濟且口語」。指揮回報不再以越短越好為預設。純確認仍可短（§2）。

### 候選
- `2026-08-18-commander-facing-voice` → promoted。

## 2026-08-18 — H4 重寫：新事實先補缺口；既有行程鎖執行者；無 Windows 不是關閉

指揮授權：思路狹窄的根因是新線索不拿去補上一刀還缺的能力。hollow「點名」H4 可被空點名過關，換成可檢查的 if-then。

### 修改
- `SKILL.md` H4：新事實先補同一執行者／同一物件的缺口；目錄能新建且已有既有行程時，`next_probe` 執行者鎖在該行程（含載入器），直到缺名被靜態分析或 host／loader DESIGN 搜尋觀測、或該注 scoped 否證。沒有原生 Windows 執行環境不是關閉、也不是換執行者的理由。
- `hunt-loop.md`／`hypothesis-engine.md`／`thinking-loop.md`／`output-contract.md`：改指新閘，刪「點名即可」。
- `scripts/test_skill_h4_gate.py`：讀 shipped `SKILL.md` 斷言新閘、拒絕舊 one-liner。

### 刪／降
- 退役 hollow H4（未點名消費者／缺名 → 不得覆寫／HTTP）。空點名不再解鎖下一探。
- 仍不寫具體載入檔名、不寫必須 Windows／ProcMon。

### 候選
- `2026-08-18-write-names-existing-consumer` → promoted（重寫後的閘；指揮明示改思維）。

## 2026-08-17 — R1：授權單位改成方向，不再一包一停

指揮授權：同意每一個 GET／POST 太碎；要批准方向，決策邊界才停。

### 修改
- `SKILL.md` R1／R3：一則訊息 = 一個已授權方向；短詞確認整個方向。
- `execution-contract.md` §2／§11.1：同方向測試取代衍生參數一律新 STEP。11.5 foothold／exploit 成功仍是決策邊界。
- thinking-loop／output-contract／hunt-loop／tactical-search／hypothesis-engine／skill-craft：跟著改「刀／包」用語。

### 刪／降
- 「一則 = 一個 Target 動作」「自然下一步也是新 STEP」「最小可區分步驟」。
- 指揮必須為同賭注覆核再點一次頭。

### 誠實邊界
- Hermes P0-RT-1 仍可能在第一個碰目標呼叫後硬停；runtime 尚未跟著放寬。
- 指揮說「STEP／一刀一停」可退回舊粒度。

## 2026-08-16 — Grok 主場：戰鬥正文減肥；Hermes 分數板移出熱路徑

指揮授權：主力在 Grok Build。第一刀瘦必載儀式，第三刀拆 Hermes 戰鬥期望。第二刀不寫 AD 食譜——目錄／域身份進 HAVE 就現場搜尋展開。

### 修改
- `SKILL.md`：授權紅線留下（一則一刀、新發現≠授權、短詞、改狀態確認、R5／R7／R8）。T／H 改成「必須為真、不必印卡」。HANDOFF 收成口語三欄；態勢列可選。
- frontmatter：Grok 觸發語（開局／掃／打這台／foothold／scope）。
- §0 熱路徑只留 hunt-loop／execution-contract／tactical-search／anti-blindspot。`p0-runtime-brief` 不在戰鬥必讀。
- `tactical-search.md`／`hunt-loop.md`：HAVE 裡的目錄／域身份／命名服務是 DESIGN 搜尋鍵，不等 Stall、不背手法表。
- thinking-loop／output-contract：去掉「必須把卡表印出來」；thinking-loop 契約段不再寫 Hermes plugin 分數。

### 刪／降
- 頂部「弱模型必載硬閘」橫幅與每則必印 T／H 表。
- 戰鬥正文裡的 Hermes plugin、7–8/10、6–7/10、`p0-runtime-brief` 指回。
- §11 戰鬥列表不再掛 runtime brief（檔仍在，改 skill／歷史才讀）。

### 未做
- 不新增 AD／ESC／BloodHound 手法表，不加第五觀察面清單。
- 不放寬 R1。不實作 P0-RT-2。

## 2026-08-16 — 狩獵循環：先觀察、搜尋展開戰術、依計畫打、每刀調整

指揮授權：副駕駛要像獵人——先看獵物，戰術即時搜尋展開（不寫死），依計畫逐步打，每刀回饋改計畫，直到狩獵成功。**未動 R1–R8 語義**（一則仍一刀；HANDOFF 停的是這一刀，不是這場狩獵）。

### 新增
- 頂部 **H1–H3 狩獵卡**（觀察完才能深打、搜尋展開才能深打、每刀必須改計畫）。
- `references/hunt-loop.md`：OBSERVE → DESIGN → EXECUTE ⇄ ADJUST → SUCCESS。
- `scripts/hunt_plan.py`：Hunt Plan 欄位、相位機、開局意圖、態勢列編解碼（機械真源）。
- 可選 overlay `./pentest-state/hunt-plan.md`（loader 印出；缺檔不降級）。

### 修改
- `tactical-search.md`：DESIGN 為主觸發，不再等 Stall 才第一次找戰術；禁止先搜分類體系名。
- thinking-loop／output-contract／stall-breaker／search-mindset／execution-contract／htb-preflight／port-scan-pipeline／anti-blindspot／hypothesis-engine／tradecraft-index／state-schemas：接到戰役相位與開局觀察 batch。
- `load_state_bundle.py`：恢復真實 `--self-test`，並驗證 hunt-plan overlay。
- 候選卡 `2026-08-14-opening-recon-batch`、`2026-08-14-source-first-not-killchain` → promoted（收進 hunt-loop §2）。

### 刪／降
- 「戰術 = Stall 時查分類頁」的主路徑（Stall 入口降為賭注打盡後的補網）。
- 開局「掃」被收成只准 rustscan 的暗示。

### 誠實邊界
- 計畫不增加本則目標 ACT。R1／R2／R3 仍在。
- 戰術內容仍不進 skill 本體。

## 2026-08-14 — HANDOFF 兩種味道（授權用盡 ≠ 能力在人）

指揮授權：交回要有「該人做」的手感，不要只剩「同意下一條 CLI」。中度契約加厚，**未動 R1–R8**。

### 修改
- `execution-contract.md` §6：從兩行 stub 換成兩種停法 + 何時選 UI + credential surface + 禁止 curl 充當看過。
- `output-contract.md`：下一步欄／風險卡／自檢補 UI 味道。
- `SKILL.md` §1、§7：各加一句指回 §6，不新增紅線。
- `error-recovery.md` GUI 層指回 `[UI]`。

### 刪／降
- 舊 §6「登入、MFA、SSO、表單優先 UI」兩行（被吸收，不再當唯一 UI 規則）。

### 候選
- `2026-08-14-handoff-flavor-ui` → promoted。

## 2026-08-14 — 弱模型適配：思維卡 + Hunter runtime

指揮授權（DanglingTree 事後分析）。目標：讓弱模型有可檢查的「怎麼想」，並在 Hermes 層擋連打；**不**再加案例、不 promote 工具食譜。

### 新增
- **R8** 通用能力先搜現成工具。
- **T1–T3** 作戰思維卡（ACT 前四欄、搜尋 SKIP 具名、新 principal = 新資產面）。
- `references/thinking-loop.md`（原 §5.0–5.2 長循環搬出 main）。
- 選配 Hermes runtime plugin（套件 id `huntspear-runtime`，本 skill 的選配 runtime plugin id）：P0-RT-1、system pin、P0-RT-5a 寫入閘（不是 huntspear skill 套件的一部分）。

### 修改
- `SKILL.md` 減法：R1／R5 長補充併回紅線一句；§5 改摘要；R3 收斂短詞語義。
- 路徑改活動根 `SKILL_ROOT`（載入的那份 SKILL.md 所在目錄／`$SKILL_DIR`），不寫死 Hermes／Claude／Grok 安裝位置。
- Hunter `tool_loop_guardrails.hard_stop_enabled=true`，`exact_failure=2`。
- `USER.md`／`MEMORY.md` 清掉單場戰鬥教訓與過期「User template 可改 SAN」誤 claim。
- 候選卡 `2026-08-13-auth-action-completion-stop`、`2026-08-13-external-material-env-specificity` → `rejected-already-covered`（已收進 R1／§2）。
- RunasCs、ADCS OID 兩張仍隔離（工具食譜／n=1）。

### 刪／降
- main 裡重複的「授權完成即停」長段（與 R1／execution-contract §11.5 去重）。
- memory 裡的 WAC／certipy／revshell 單場筆記。

### 誠實邊界
- P0-RT-2 未完成。期望值約 7–8/10，不是 9/10。
- 新 session 才吃到 plugin pin 與新 USER.md。

## 2026-08-11 — Respawn：加入紅線／學習回路／P0-RT-5

把 huntspear 從「搜尋驅動狩獵副駕駛」升級為 respawn 後的單一真源戰鬥主檔。
frontmatter `name: huntspear`；`description` 改寫反映 respawn 設計。
設計：搜尋驅動精簡脊椎 + redthread 8/11 硬化過的可機械判定閘門 + 一條全新學習回路。
共識來源：2026-08-11 Hunter × Claude。

### 新增
- **頂部 🔴 回合紅線 R1–R7**（弱模型必載硬閘），每條帶祖先註記（redthread 鐵律 §N + 本 skill 舊 §M）。
- **§10 學習回路閘門**（可機械判定 5 句）+ `references/learning-loop.md`（六步 + 三污染防護 + 候選卡 schema + 三級共識 + 紅線自審）。
- `references/tradecraft-index.md`（薄索引 + 症狀決策樹，不複製心法內容）。
- `references/anti-blindspot.md`（移植 redthread；唯一 curated 心法 ref，槓桿最高；已改 cross-ref 指向 tactical-search/態勢列）。
- `references/htb-preflight.md`（移植 redthread；已改 cross-ref 指向 tactical-search/anti-blindspot）。
- `references/port-scan-pipeline.md`（移植 redthread；USER.md 日常「掃+詳細度」需求；已改 recon-attack-surface→tactical-search、goal_attempts→態勢列 attempts）。
- `references/skill-craft.md`（合併 redthread-craft 6 工藝條 + pentest-copilot 的 anti-blindspot design／named-peer auth／craft 輸出風格／Pitfalls；丟棄 version 號、redthread-dev 路徑、Improvement Waves、communitytools clone）。
- `references/p0-runtime-brief.md`（P0-RT-1..4 移植 redthread + **新增 P0-RT-5：skill 檔寫入閘 + 學習回路升級 lint**）。
- `references/candidate-patches/`（學習回路隔離暫存區，`.gitkeep` 標記）。

### 修改
- `SKILL.md`：全檔重排。頂部紅線 → §0 progressive disclosure（新增 6 條路由）→ §1–§9 重排補指回 → §10 學習回路。§7 輸出格式加入**態勢列**與**回合結尾自檢**。§4 加「domain ref 是學習回路產物不是起始庫存」設計註。
- `references/execution-contract.md`：新增 §11（衍生參數測試 / 同面測試 / 授權時效 / 失敗兩次停），對應 R1/R3/R5。
- `references/output-contract.md`：新增 §9 態勢列、§10 回合結尾自檢（6 條紅線對照）。

### 未改（保留原樣）
- 心法 ref：`search-mindset.md`、`tactical-search.md`、`hypothesis-engine.md`、`stall-breaker.md`。
- `state-schemas.md`、`error-recovery.md`、`scripts/load_state_bundle.py`。

### 誠實邊界
- 弱模型 HITL 上限仍約 6–7/10（純文字）；到 9/10 需 runtime（P0-RT-1..5）。學習回路**不改變**此天花板。
- auto-detect + auto-draft（進隔離區）= 開；**auto-promote（落 canonical）= 關**，直到 P0-RT-5 到位。
