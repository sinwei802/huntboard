# Candidate Patch: 2026-09-16 — checkpoint 是寫事實再 stamp

Trigger:            指揮說「紀錄進度」，副駕駛對 schema 反覆試錯。指揮：「不就寫文字？？？」
Class:              contract
Raw-observation:    Management 第一個 checkpoint：讀 state-schemas、試 metadata、卡住。五核心檔有嚴格 schema，沒有寫入腳本。
Generalized-claim:  保存進度＝把事實寫進正文，再跑 loader `--stamp` 對齊 metadata／補空骨架。禁止為對格式去讀 schema 或腳本源碼。stamp 失敗才讀欄位說明。
Sightings(n=1):     本場 checkpoint。指揮明示改 skill；這是摩擦不是戰術，反例測試不會縮小攻擊面。
Reverse-test:       不會自動寫入：仍只有指揮明確要求才 stamp。不把「繼續」當保存。
De-specified:       問題軸：保存進度的戰鬥路徑是寫事實還是考古格式？
Target-file:        SKILL.md §3／§0；state-schemas.md；scripts/load_state_bundle.py
Consensus-tier:     中度（契約／工具；不碰 R1–R8）
Status:             superseded（2026-09-21-checkpoint-write-once；手寫再 stamp 仍造成重試）
Subtraction:        戰鬥路徑刪「要改 checkpoint 規則才讀 state-schemas」。
