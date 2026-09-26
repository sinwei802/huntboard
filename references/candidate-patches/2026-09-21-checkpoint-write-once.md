# Candidate Patch: 2026-09-21 — checkpoint 一次寫入

Trigger:            指揮說紀錄進度後出現大量寫入／修格式，應一次寫入或更新
Class:              contract
Raw-observation:    Phantom checkpoint 28 次工具、19 輪模型、約 320 萬 token：stamp → 格式不過 → 讀 schema → 補丁。Management 2026-09-16 同一摩擦，當時 promote「手寫再 stamp」。
Generalized-claim:  保存進度＝一份 facts JSON 跑寫入腳本，產出合法 bundle 並驗證後才覆蓋。失敗原檔不動。戰鬥禁止手寫核心檔、禁止為對格式讀 schema。失敗一次改 JSON 再跑；第二次停。
Sightings(n=2):     (1) Management 第一個 checkpoint 卡 schema；(2) Phantom cp-20260921-123442 重試鏈。
Reverse-test:       不會自動寫入：仍只有指揮明確要求才跑。不把「繼續」當保存。
De-specified:       問題軸：保存進度是一次渲染還是對格式考古？
Target-file:        scripts/checkpoint_write.py；SKILL.md §3；state-schemas.md Checkpoint
Consensus-tier:     中度（契約／工具；未縮小攻擊面）
Status:             promoted（指揮 2026-09-21 點 C1）
Subtraction:        戰鬥路徑「手寫正文再 stamp」；「stamp 失敗才讀 schema」。
