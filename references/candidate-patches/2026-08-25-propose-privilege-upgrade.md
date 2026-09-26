# Candidate Patch: 2026-08-25 — 判斷升級更能改 Goal 時必須提出，不得只在低權限打轉

Trigger:            指揮問：若更高權限更好，為什麼不提出來請我授權？
Class:              contract
Raw-observation:    已有 PHP RCE。副駕駛把 OS 命令／phpinfo 從下一步拿掉，只交 DNS／unlink，在已批准的低權限裡打轉。指揮事後說：需要更高權限就該問，不要替指揮把選項刪掉。
Generalized-claim:  「最便宜且能改 Goal」以達成 Goal 計，不是以留在當前授權的動作類裡計。若執行者判斷權限／能力升級比同權限再探更便宜，HANDOFF 必須把該升級寫成具名 CONFIRM 選項（可當主下一探）。提出≠執行。不得只交低權限變體當唯一出路。
Sightings(n=2):     (1) 2026-08-25 假客服：RCE 後不提 OS 命令，只 DNS；(2) 2026-08-14 開局寬度：未認證列舉被拆成多次點頭，直到指揮說允許 batch。
Reverse-test:       不會要求每個 GET 200 都提議 RCE。沒有判斷「升級更便宜」就不必發明升級。提出後仍要指揮點名才可 ACT（R1／R4 不變）。
De-specified:       問題軸：下一探按「Goal 最便宜」還是「當前授權內最便宜」排序？
Target-file:        SKILL.md §2／§7／§9；hunt-loop.md §3；output-contract.md 自檢
Consensus-tier:     中度（HANDOFF 下一步組成；未動 R1–R8）
Status:             promoted
Subtraction:        刪「最便宜＝留在已批准動作類裡」的讀法。不新增 R 編號、不寫 OS shell 食譜。
