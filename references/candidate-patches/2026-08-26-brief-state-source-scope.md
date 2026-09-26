# Candidate Patch: 2026-08-26 — 狀態摘要載入；Source-first 限本場；砍 SKILL 複本

Trigger:            指揮授權改進 token 浪費與邏輯衝突。第一刀對準三個真源打架，不是再貼「省 token」。
Class:              contract
Raw-observation:    `load_state_bundle.py` 開局把五個核心檔全文倒進對話，但 SKILL 說「一兩句話交代」、state-schemas 說 evidence 按需。Source-first 寫「讀完目前可及的來源」，模型把舊案 writeup／JS bundle／源碼樹當「已在手」。SKILL §1.2 表、§9 禁止清單、§11 檔名菜單與 R／H／execution-contract／§0 重複。
Generalized-claim:  啟動狀態輸出預設是摘要。Source-first 的範圍是本 engagement。always-loaded 的 SKILL.md 只留閘門與獨特原則，否定句不重抄紅線。
Sightings(n=2):     (1) 20260825 Grok 開局 loader 8–18KB 狀態牆 + 讀 20260714 源碼樹；(2) SKILL.md 270 行裡 §9 整節是 R1–R8／H1–H4／§2 的否定句。
Reverse-test:       不刪五核心檔、不讓啟動變成「不恢復狀態」。`--full` 仍可倒正文。不把 source-first 廢成可以不讀本場材料。不把 R／H 移出 main。
De-specified:       問題軸：狀態與材料是「凡能讀就整份灌進 context」還是「本場、按需、摘要優先」？
Target-file:        scripts/load_state_bundle.py；SKILL.md §1.2／§2／§3／§9／§11；hunt-loop.md §2.2；state-schemas.md；thinking-loop.md；tradecraft-index.md；htb-preflight.md
Consensus-tier:     中度（載入與攝入範圍；未動 R1–R8）
Status:             promoted
Subtraction:        刪 SKILL §11 References 菜單；刪 §1.2 與 execution-contract 重複的 approval 表；刪 §9 裡重抄 R／H／§2 的否定句；loader 預設不再倒核心檔正文。
