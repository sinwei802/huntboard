# Learning Loop — 學習回路詳解（收尾-time 自我維護）

> 對應 SKILL §10 閘門版。§10 是可機械判定的 5 句；本檔是六步全流程 + 三污染防護 + 候選卡 schema + 三級共識。
> **核心心法**：回路寫的是「心法／問題軸／閘門措辭」的可泛化教訓，**不是**「這次用什麼工具打了哪台機」。
> target-specific 敘事進 `md-hacking-writeup` 與 search cache，**永不進 skill 本體**。

## 0. 何時跑

- 收尾觸發：root / flag / 交報告 / 驗收通過；或使用者明說「記下這次／學一下這次」。
- 收尾**不**自動改 canonical；預設只呈「隔離區候選清單」給指揮，靜默升級零。

## 1. 六步全流程

1. **HARVEST（收割）**
   - 來源：本場 engagement 的 Stall 診斷、失敗軸、被推翻的假設、`md-hacking-writeup` 的 Phase artifact（雙向-讀接縫）。
   - 產物：原始觀測（raw observation），先不判斷泛化性。

2. **CLASSIFY（分類到目標檔）**
   - `gate → 回合紅線 R1–R8`（最高門檻，雙強共識，n≥3）
   - `mindset → 心法層 ref`（anti-blindspot / hunt-loop / hypothesis-engine / search-mindset / stall-breaker）
   - `route → tactical-search 搜尋鍵擴充`，或（罕見）promote 出一份**新的 question-generator route ref**（僅當某組正交軸通過 n≥2 且確為可重用軸集）
   - `contract → execution／output／state`（重大）
   - `craft → skill-craft.md`（工藝條本身的精煉）

3. **QUARANTINE（隔離）**
   - 一律先寫 `references/candidate-patches/YYYY-MM-DD-<slug>.md`，**不落 canonical**。
   - 隔離區可見、可逆、有記錄；auto-detect + auto-draft 可自動起草進此區（Q7 開）。

4. **GENERALIZATION TEST（泛化測試三問，可機械判定）**
   - (i) **n**：有 ≥2 個獨立情境支持？（心法／route n≥2；碰紅線的 gate n≥3；n 不足留隔離區等第 2 次目擊）
   - (ii) **反例測試**：在別的目標上套用會害事嗎？會 → 這是**偏好**不是規則（偏好至多變 illustration，永不變 gate）。
   - (iii) **去具體化**：抽掉具體工具／IP／版本後，剩下的是**問題軸**還是**斷言**？斷言拒收（斷言＝寫死一條「答案」）。

5. **PROMOTE（升級）**
   - 過測 + 若屬「重大」需**雙強共識** → 才動 canonical。**靜默升級 = 違規。**
   - **減法義務（硬步驟）**：每次 PROMOTE pass 必須顯式回答「這次要刪／降級為 illustration 什麼？」淨行數成長 ≈ 零或負。答案是「無」也要寫出。
   - **auto-promote（落 canonical）維持關**，直到 `p0-runtime-brief.md` P0-RT-5 到位（寫入閘 + 升級 lint）。

6. **指揮權（HANDOFF）**
   - 收尾預設只呈隔離區候選清單 + 每張卡的四態結論之一，交還指揮。

## 2. 三種污染防護

1. **一次性環境特殊性**：n=1 的觀測不進本體（留隔離區等第 2 次獨立目擊）。
2. **使用者偏好污染**：技術偏好至多變 illustration，**永不變 gate**；互動／輸出偏好（例如「先給態勢列」）可成規則。判準＝反例測試 (ii)。
3. **弱模型犯規補償污染**：弱模型的違規先進 `p0-runtime-brief.md` 的 runtime backlog，**不**進戰鬥 skill 文字（別為了補一個弱模型 bug 而在紅線上再堆反例，堆反例稀釋位置價值）。

## 3. 候選教訓卡 schema

每張 `candidate-patches/YYYY-MM-DD-<slug>.md` 至少含：

```text
Trigger:            觸發這條教訓的情境（一句）
Class:              gate | mindset | route | contract | craft
Raw-observation:    原始觀測（可含 target-specific 細節，僅供推導）
Generalized-claim:  去具體化後的可泛化主張（問題軸語言）
Sightings(n=?):     幾個獨立情境見過（附各自一句）
Reverse-test:       在別的目標會害事嗎？（會/不會 + 一句）
De-specified:       抽掉具體後剩問題軸還是斷言？
Target-file:        若升級，落哪個 canonical 檔
Consensus-tier:     一般 | 中度 | 重大
Status:             quarantined | promoted | rejected-target-specific | rejected-already-covered
Subtraction:        本次 PROMOTE 要刪/降級什麼（含「無」）
```

跑完一張卡，結論必為四者之一：`{promoted | quarantined-needs-2nd-sighting | rejected-target-specific | rejected-already-covered}`，且由欄位機械導出。**一個只會 promote、從不 reject 的回路就是 bloat 引擎。**

## 4. 三級共識

| 級 | 觸發 | 需求 |
|----|------|------|
| **一般** | 加一個示例、補一句 illustration | 免共識，可直接動（仍記錄） |
| **中度** | 加問題軸、動情境層 ref、擴 tactical-search 分類 | 單人審 + 記錄；加示例可免 |
| **重大** | 碰紅線 R1–R8／縮小攻擊面／動契約層／退役合併 skill／改核心循環心法 | **雙強共識**（named-peer auth 必須通；auth fail → STOP + HANDOFF，不 silent fallback） |

## 5. 紅線自審（脫離框架後新增）

紅線從出生就屬於 huntboard、沒有跨 skill 的 dual-consensus 指回要保護，故回路可定期跑一次「紅線自審」：用 `skill-craft.md` 檢查清單逐條驗（可數嗎？類別非工具名？去重了嗎？措辭對弱模型有歧義嗎？）並**提議**收緊／放鬆。落地仍走雙強共識，但**提議本身**現在合法。
