# Candidate Patch: 2026-09-14 — 查庫不是開局儀式

Trigger:            指揮問開局查 Obsidian 會不會耗 token，並授權依建議改。
Class:              contract
Raw-observation:    §3「每次啟動」旁寫開局查 evidence-db。紙面上限是索引一次＋最多 1 實體頁，但觸發是儀式、查詢靠組另一個 skill。08-25 已見過模型把查庫做成讀舊案 writeup／源碼樹。CTF 沒有 skip。evidence-db 自己寫「收工才進庫」，兩邊不一致。
Generalized-claim:  跨案件查庫的觸發是「本場第一次見到可索引 IOC」，不是 session start。CTF／無 IOC → 0 次讀 vault。戰鬥中只跑腳本搜索引；模型不 `read_file` vault、不載 evidence-db。寫庫仍只在收尾。
Sightings(n=2):     (1) 20260825 開局查庫被執行成 20260714 writeup／PHP 源碼樹；(2) 2026-09-14 設計核對：索引 4KB、案件筆記單篇可達 63KB，貴的是 wikilink 另一頭。
Reverse-test:       不刪跨案件 IOC 查詢。打詐第一眼見到 IP／域名仍可查。收尾仍用 evidence-db 寫庫。不把 source-first 放寬成可以不讀本場材料。
De-specified:       問題軸：vault 是「開局流程的一環」還是「有 IOC 時的機械索引查詢」？
Target-file:        SKILL.md §0／§3／§8／§10；scripts/ioc_lookup.py；evidence-db SKILL.md 關係句
Consensus-tier:     中度（載入閘；未動 R1–R8）
Status:             promoted
Subtraction:        刪「開局查證據資料庫」；刪戰鬥中「用 evidence-db 的總索引查一次／命中再讀實體頁」；刪開局讀舊案 writeup 的但書（改成模型不進 vault）。
