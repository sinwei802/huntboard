# Candidate Patch: 2026-09-16 — 變體矩陣不是 HTTP 專用

Trigger:            同一 primitive 的 argv／旗標變體被拆成多則確認；HTTP 矩陣卻一次跑完
Class:              mindset
Raw-observation:    Management：jato.clientSession 通道／編碼一次跑。rdiff-backup 的 path／mode／list／backup 拆成 H-14…H-20，指揮多次「同意」，最後口述「* 就是後面可接任意 arg」。
Generalized-claim:  §4.1 的通道／編碼是 illustration。同一組 expect／kill_if 的變體（通道、編碼、argv、旗標、路徑、mode、API version）是一個方向的偵查，不是一串請示。
Sightings(n=2):     (1) 08-25 指揮要求 HTTP 通道一次跑完。(2) Management sudo 額外 arg 被拆成多則。
Reverse-test:       不會變成整條殺傷鏈：R1 的信任邊界／動作類升級／新秘密使用仍停。read-only 與 root 寫入仍是不同動作類。
De-specified:       問題軸：什麼算同一方向的變體？不是「sudo * 一定 last-wins」。
Target-file:        SKILL.md §2／§7；hunt-loop.md §4.1；execution-contract.md 並列探查
Consensus-tier:     中度
Status:             promoted（指揮 2026-09-16 授權改 skill，保持心法）
Subtraction:        HTTP query／Cookie／Header 從閘降為 illustration。刪 pearcmd 示例。
