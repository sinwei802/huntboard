# Candidate Patch: 2026-09-23 — 已讀名單用腳本記；brief 不倒計畫正文

Trigger:            指揮要在保住狩獵能力的前提下降低 token。實測大頭是同一份材料進對話後每輪重播，不是 SKILL 前綴本身。
Class:              contract
Raw-observation:    2026-08-25：execution-contract 同場讀 10 次、腳本源碼與截圖進上下文，峰值 33–35 萬。session-once 只寫在文章裡。loader brief 仍把 hunt-plan.md 整份印出。
Generalized-claim:  本對話已讀哪些 reference，用腳本名單＋內容雜湊回答，不靠模型記得。換 session 或 compact／new 後名單不作數。狀態摘要帶決策需要的態勢與活躍賭注，不帶計畫全文。
Sightings(n=2):     (1) 2026-08-25 兩場 Grok 狩獵的重讀；(2) 2026-09-23 架構討論，確認帳在歷史重播，brief overlay 仍是固定漏口。
Reverse-test:       不刪 R1–R8／H1–H4。不把閘門搬出 SKILL.md。compact 後必須能重讀，所以 reset 跟 compact 綁在一起。沒有 session id 時不假裝已讀。`--full` 仍可倒正文。
De-specified:       問題軸：已讀是本對話的事實還是模型的記憶？摘要要帶哪些決策欄、哪些留在磁碟？
Target-file:        SKILL.md §0／§3／§7；state-schemas.md；scripts/hunt_plan.py；scripts/load_state_bundle.py
Consensus-tier:     中度（載入與狀態摘要；未動 R1–R8）
Status:             promoted
Subtraction:        刪 brief 的 hunt-plan 全文傾印。不新增紅線編號、不寫省 token 空話、不把名單寫進 pentest-state。
