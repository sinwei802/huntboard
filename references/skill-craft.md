# Skill Craft — 弱模型適配工藝條（合併 redthread-craft + pentest-copilot）

> **不是戰鬥 skill、是 skill 作者的工藝參考。** 載入時機：你正在設計／修改本 skill 的紅線／閘門／HITL 規則，且目標讀者含弱模型（deepseek / mini / haiku 等）。不自動注入。
> 來源合併：redthread-craft 6 工藝條（canonical）+ pentest-copilot-skill-craft 的 anti-blindspot design／named-peer auth／craft 輸出風格／Pitfalls。
> 已丟棄：`version:` 版本號（rolling 慣例不寫版本）、`redthread-dev` workspace 路徑、Improvement Waves、communitytools clone——這些是舊 workspace 遺物，與 huntspear 無關。

## 1. 六條核心工藝條（canonical）

### 1.1 閘門位置上移 main skill（progressive disclosure 對弱模型無效）
弱模型「該不該載入 reference」的判斷正是失敗的那件事——它傾向不載入。所以 HITL 紅線、衝突裁決、授權時效、寫入閘、失敗 2 次停**必須**在 main `SKILL.md` 頂部，不能只放 reference。main 寫精簡可機械判定短句 + 一句指回；reference 寫長反例。
（huntspear 落實：頂部 🔴 R1–R8 必載區 + 🧠 T1–T3 思維卡。十二步長循環在 `thinking-loop.md`，不佔 main。）

### 1.2 可機械判定 vs 判斷題
弱模型對判斷題永遠選對自己寬鬆的那邊。用可數／可機械判定的測試取代「算不算」：
- 「算不算還能打」→ **同方向測試**（同一賭注 + 動作類不升級 + 目標已點名或只是覆核剛寫入的 + 不用新秘密；任一失敗 → 新方向）
- 「是不是同語義失敗」→ **同一 error 類別 ×2 → HANDOFF**（不細分工具）
- 「算不算改目標狀態」→ **會留下痕跡或改變狀態的動作一律 CONFIRM-REQUIRED**
- 禁用「通常／一般／視情況」——規範條目裡等於沒寫。

### 1.3 類別錨定，不要列工具清單
清單永遠不完備，弱模型碰清單外工具會推論「不在禁止清單＝可以」。錨在三類動作：`目標寫入`／`憑證使用`／`exploit・PoC 執行`。工具名只當 illustration，永遠加「包括但不限於，判準看類別不看工具名」。

### 1.4 契約 vs 強制（誠實邊界）
skill 文字是**契約性宣告**、不是機械保證。明確分「契約宣告」與「runtime 強制」，給期望值（如「弱模型 HITL 上限約 6–7/10；到 9/10 需 runtime 硬停」），禁止「已鎖死／保證」這類絕對詞除非真有 runtime 配合。
（huntspear 落實：R6 誠實邊界橫幅 + `p0-runtime-brief.md`。）

### 1.5 可數 vs 不可數
可數語句要明確啟動條件：「同一 error 類別連續 2 次 → 必須 HANDOFF」寫成「計數 = 2 時觸發，下一步必須 HANDOFF，禁止第 3 次」。「缺標籤視同未完成 HANDOFF」必須在 main、不只在 reference。
（huntspear 落實：R2/R3 刻意分開，因為「新發現≠授權」與「授權時效」是兩種不同誤讀模式。）

### 1.6 去重（不要把同一條寫在四處）
弱模型遇矛盾選寬鬆那邊；多處重複也稀釋 main 最重要的幾條。canonical 一份（通常 main 頂部）+ 詳解一份（reference）+ 其他處改為「詳 §X」指回。每次加新規則前先 `grep`。

## 2. Anti-blindspot design（class rules，來自 pentest-copilot）

長 technique 清單製造 *coverage illusion*——模型把 skill 當閉合宇宙，新技術變盲點；只砍清單不加流程只是把盲點移到 training-memory playbook。編輯 route／心法 ref 時：

1. 優先「核心問題 + 正交軸 + 怎麼 mint 假設 + 搜尋槽 + 症狀→下一問」。
2. 具名手法 = **optional illustration only**，永不當 gate（禁「必須做完 A→E」）。
3. 明寫一行：*未寫入的技術預設可能存在；禁止因表上沒有而排除*。
4. **看似熟悉陷阱**：常見 SMB／Web／AD 外形在發經典 exploit Target STEP 前，仍需 NAMING 或 ≥1 條 behavior/primitive lens（`anti-blindspot.md` §2.1）。
5. 改薄 route 後 `grep` 死連結（`§1.1`、舊標題）於 SKILL/output/error——斷連結會復活 memory playbook。
6. 不要一邊薄 route 一邊留一份肥 cookbook（雙厚度重建幻覺）。

## 3. Named-peer auth（雙強共識依賴，來自 pentest-copilot）

使用者指名 Claude（或其他 peer）做共識 → **只**用那個 peer。auth／tool 失敗 → **STOP + HANDOFF**，不 silent 換 OpenCode／Codex／其他 CLI，不 thrash。**使用者把 silent fallback 等同於弱模型 run-on。** 雙強共識的可用性 = named-peer auth 的可用性；重大級無法落地時只能停等，不得繞道。

## 4. 評估現有 skill 可遵守性（0–10）

依序跑：位置檢查 → 可數檢查（改寫成 if-then）→ 類別檢查（動作類別 vs 工具清單）→ 去重檢查（grep）→ 誠實邊界（有無絕對詞、runtime 配合有無寫）→ 三句測試（不懂 context 的審閱者 30 秒內能說出三條最重要規則嗎）。
- 9–10：閘門在 main、可數、類別、去重、誠實邊界、runtime 配合皆到位。
- 5–6：閘門在 main 但有判斷題或誠實邊界不明。
- 0–2：閘門散落、無誠實邊界、模型完全不遵守。

## 5. Craft session 輸出風格（來自 pentest-copilot）

- 先給決策與檔案清單；表格優於長文。
- 分析後給明確下一個選擇，**或**已獲階段授權就實作。
- 同步問題講清楚；絕不 silent 覆寫 live。
- 治理一整**類**任務的偏好教訓進 skill body（或本工藝條），不只進 memory。

## 6. Pitfalls（精選自 pentest-copilot，去掉舊 workspace 專屬項）

- 硬 gate 只放在未載入的 reference 卻宣稱「弱模型鎖死」。
- 「一則一個方向」旁邊又寫「每包都停」（矛盾對，模型選鬆的或選碎的）。
- 工具名 deny-list 而非動作類別。
- named-peer auth 失敗 → silent 換 CLI（＝弱模型 run-on）。
- 宣稱「文字已壓過 finish-the-job」卻無 runtime backlog。
- 薄 route 旁留肥 cookbook；rewrite 後留死 § 連結。
- depth／persist 綁死（每次「掃」都強建 `./scan`）。
- 該進 class skill 的教訓只寫進 memory。

## 7. 維護

- 不寫版本號（rolling，隨共識更新）。
- 重大更新需雙強共識才寫入本檔的規範段落。
- 引用：`p0-runtime-brief.md`、學習回路 `learning-loop.md`、DanglingTree 弱模型違規樣本（2026-08-11）。
