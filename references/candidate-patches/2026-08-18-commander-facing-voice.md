# Candidate Patch: 2026-08-18 — 對指揮的回報要好懂，不要密語精簡

Trigger:            指揮回報「用語不太好懂」；執行者技術強於指揮時，三欄寫成內部密語／過短疊句
Class:              contract
Raw-observation:    副駕駛用「執行者／缺名／scoped 否證／H4」交差，指揮跟不上。skill 原本寫「輸出經濟」，模型把它收成越短越好。
Generalized-claim:  對指揮的 HANDOFF 先寫看到什麼、為什麼重要、接下來要試什麼；術語第一次用人話解釋；一句一事；講到指揮能複述為止。命令與識別名保持原樣。不要把內部閘門編號當正文。輸出偏好可成規則（學習回路：互動／輸出偏好）。
Sightings(n=2):     (1) 本場指揮明說用語難懂、不要過精簡；(2) skill 既有「禁止電報文」仍被「經濟」壓過，三欄繼續密語。
Reverse-test:       不會要求把命令意譯，也不要求每個 HTTP 200 寫長文。純確認仍可短。會害事的是把戰術食譜寫進回報規則。
De-specified:       問題軸：對能力較弱的決策者，回報密度跟誰對齊？
Target-file:        SKILL.md 輸出原則／§7；output-contract.md §1.1 與自檢 13
Consensus-tier:     一般（輸出偏好成規則）
Status:             promoted
Subtraction:        刪 SKILL「輸出經濟且口語」。經濟不再是指揮回報的預設。
