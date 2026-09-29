# Thinking Loop — 核心循環詳解

> **不是戰鬥熱路徑。** 改本 skill 的循環內部步驟、或除錯「卡片與現況對不上」時才讀。  
> 指揮不需要看到十二步。授權與戰役閘在 `SKILL.md`（必須為真，不必印卡）。本檔是展開，不是第二套規則。  
> 戰役相位與開局觀察在 `hunt-loop.md`。

## 1. 何謂「新情報」

完整循環**只**在下列情況從頭跑一次：

- 使用者發來**新訊息**；或
- 使用者已授權方向的**停條件已到**後，需要整理並 HANDOFF。

下列**不是**新情報，**禁止**因此重開 HYDRATE→…→ACT：

- 中間 tool 回傳（search、fetch、read、shell 輸出等）
- 讀完某份 reference
- 假設組合在作業脈絡內的改寫

方向進行中，tool 回傳後先 INTERPRET：未到決策邊界可繼續同方向覆核。  
停條件一到**只允許**：H3 改計畫 →（僅當本則剛完成觀察且預算仍有：DESIGN 搜尋）→（可選 Stall **文字**診斷）→ **HANDOFF 並停止**。  
禁止因 tool 結果開新方向（R1）。除「觀察剛完成的 DESIGN 搜尋」外，禁止再開一輪搜尋。

## 2. 步驟（使用者新訊息時）

1. **HYDRATE** — 跑 `warboard.py opening`／`brief`（預設摘要，不倒 markdown 正文）；繼承的 closed／BLOCKED 若缺 scoped 反證，標待重驗，不當永久牆
2. **PREFLIGHT** — 新 HTB／lab 目標或連線未驗證時，載入 `htb-preflight.md` 做最小連通／hosts／archetype 檢查；缺 VPN／hosts 把命令交給指揮，preflight 完成後 STOP，不同輪自動掃描
3. **PARSE** — 提取已知目標、服務、版本、錯誤、材料、已做過的事。先盤 `HAVE`（手上已有的 identity／通道），不要先盤「想打什麼」。判定狩獵相位；開局口語走 `hunt-loop.md` §2.1
4. **STATE** — 只在作業脈絡更新 Asset Graph、Route Stack、Loot Tracker、Evidence Index、Hunt Plan。新否證與舊 claim 衝突時必須改寫舊 claim，不得並存
5. **HYPOTHESIS PORTFOLIO** — 維持 2–3 條正交賭注；每條必須有支持證據、缺少前提、最小否證條件（純推理，不因此開搜）。已有 Hunt Plan 則繼承並排序。詳 `hypothesis-engine.md`
6. **SEARCH DECISION** — 搜尋是正常路徑。作業脈絡要能說出 `SEARCH:` 或三個合法跳過理由之一。工具參數／hash mode／詞表／規則檔不得跳過。觀察已完且無計畫，或 HAVE 裡有尚未展開的目錄／域身份 → DESIGN（`tactical-search.md`）。一般知識用 `search-mindset.md`
7. **CHOOSE** — 下一刀必須是計畫上的 `next_probe`（或 H3 已寫明的改探）。通用能力先搜現成工具（R8）。若下一探是「一條 primitive 成不成立」，先組變體軸／對照矩陣，用腳本一次跑（`hunt-loop.md` §4.1），不要每格當新方向
8. **ACT 前自檢**
   - 是否需讀 `execution-contract.md`？（載入時機見該檔開頭）
   - 授權是否仍成立？（R2／R3）
   - 新 principal 的資產類是否已點名？
   - 深打是否過 H1／H2？（觀察完 + Hunt Plan）。新事實是否先補上一刀缺口？目錄能新建且已有既有行程時，下一探執行者是否仍是那個行程、缺名是否已靜態分析或 DESIGN 搜尋觀測？（H4）。卡表不必印給指揮
9. **ACT**
   - **僅** `PRE-AUTHORIZED` 才執行目標動作
   - 否則輸出風險確認卡並**等待**——本回合 **0** 次目標 tool call
   - 每個使用者訊息最多 **1** 個已授權方向（指揮要求一刀一停時退回單動作）
   - 開局觀察方向只准未認證取樣，不得含 exploit
10. **INTERPRET + FALSIFY CHECK** — 更新事實；觸及否證條件則降級或關閉並寫明 scope（含「從哪個 identity 看的」）。新秘密／新身份／新信任邊界：停止使用（R2）。同方向覆核讀面可繼續直到決策邊界。停條件一到才填 H3 並改寫 Hunt Plan
11. **STALL CHECK** — 連續 3 個已完成 STEP 的 outcome 皆非 `fact_gained`／`new_surface` → Stall-Breaker **診斷**（除非已跳過）。先看觀察缺口與未測賭注。診斷產出的否證測試預設 `CONFIRM-REQUIRED`
12. **HANDOFF** — 口語選項欄回報（2–3 條已排序；建議那條寫完整；態勢列）並交還指揮權。**此後禁止任何 tool call**。下一則從這份計畫接著打，直到 SUCCESS

## 3. 回合邊界（執行層；與 R1 衝突時以 R1 為準）

1. **單一使用者訊息**最多完成下列之一，然後必須 HANDOFF：
   - 有界研究（搜尋／讀 ref／本地分析），**0** 次目標 ACT；或
   - **1** 個已授權方向，直到決策邊界；或
   - Stall 文字診斷 + **1 個**提案方向（不執行，除非已具名授權）
2. 方向進行中可繼續同方向覆核。停條件一到：INTERPRET + H3 →（僅當本則剛完成觀察：可 DESIGN 搜尋）→（可選 Stall 文字）→ HANDOFF
3. **HANDOFF 之後：禁止任何 tool call**
4. `CONFIRM-REQUIRED`：只出風險卡，**0** 目標 tool call
5. 研究結果只改變假設與排序，**不得**在同輪自動觸發目標動作。觀察剛完成時允許同則 DESIGN 搜尋，仍不得同則深打
6. 不得用 shell `&&`／`;`／腳本把跨信任邊界或動作類升級藏成「同一方向」。同一賭注的偵查矩陣用腳本一次跑是合法的（`hunt-loop.md` §4.1）
7. 方向的停條件一到（成功或失敗），該授權已用盡

## 4. 契約

本檔與 `SKILL.md` 是契約。決策邊界優先於「作完再停」。沒有 runtime 代擋跨方向連打——文字說停就停。
