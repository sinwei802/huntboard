# Candidate Patch: 2026-08-25 — Session-once 載入；材料攝入有上限

Trigger:            指揮問今天 Grok token 為什麼那麼重。自我檢查：兩場狩獵 0 compact、峰值 33–35 萬、329 次 API、prompt 累計 5670 萬。
Class:              contract
Raw-observation:    §0 已寫「不要預載」，開局仍把 SKILL.md／execution-contract（同場 10 次）／hunt_plan.py 源碼／load_state_bundle.py 源碼／CHANGELOG 讀完。契約寫「ACT 前若本輪尚未讀過必須先讀」，模型把「本輪」當成每一批 tool call。截圖要求被執行成 `read_file` PNG。開局查 evidence-db 被執行成把舊案 writeup／PHP 源碼樹拉進來。
Generalized-claim:  載入閘是 session-once，不是每批 ACT 一次。腳本只執行不讀源碼。已注入的 SKILL.md 禁止再讀。跨案件只查本場已見 IOC 的索引，命中最多 1 個實體頁。截圖存檔＋HANDOFF 給路徑，預設不把圖灌進模型。相位邊界建議 `/compact` 或 `/new`。
Sightings(n=2):     (1) 20260825_711 Grok 偵查：execution-contract×10、開局讀 20260714_bb writeup／源碼；(2) 20260825_date Grok 狩獵：三張 PNG 灌進 context、grok 與 claude 兩份 huntboard 各讀一遍（其實是同一 symlink）。
Reverse-test:       不刪截圖義務、不刪 evidence-db、不放寬 R1。升級動作類／高風險 CONFIRM 仍要讀 execution-contract（每 session 一次）。畫面判斷真的依賴驗證碼／彈窗／consent 且 dump-dom 不夠時仍可把圖送進模型。
De-specified:       問題軸：references 與材料是「每次 ACT 再載」還是「本場一次＋攝入上限」？
Target-file:        SKILL.md §0／§3／§7；execution-contract.md 開頭；hunt-loop.md §2.3；output-contract.md；thinking-loop.md ACT 前自檢；tradecraft-index.md；port-scan-pipeline.md §0
Consensus-tier:     中度（載入閘；未動 R1–R8）
Status:             promoted
Subtraction:        刪「ACT 前若本輪尚未讀過本文件，必須先讀」；刪「即將 ACT 必讀 execution-contract」；刪「HANDOFF 必須內嵌圖／給指揮看圖」。不新增 R 編號、不寫省 token 空話。
