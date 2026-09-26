# Candidate Patch: 2026-08-26 — 採納 Claude 契約審查（收緊 R2，其餘去重／可數化）

Trigger:            指揮同意採納 Fable 審查；R2 不用審查原句（那句會讓本則新密碼當參數）。
Class:              contract
Raw-observation:    always-loaded 把「不等 Stall」抄四次；Stall「重要事實」不可數；§2 升級當主下一探與 H4 鎖執行者互打；11.5a 弱模型讀成收工；指揮態勢列洩漏 Phase；R2 與已點名動作類的同回合研究死鎖。
Generalized-claim:  戰術觸發只留 H2。Stall 用 outcome 枚舉。升級只當 CONFIRM，不取代未關的 H4 next_probe。R2 擋的是本則新秘密的**使用**，已點名動作類可同回合查怎麼做。里程碑 HANDOFF 是換方向不是收工。指揮態勢列不含 Phase。
Sightings(n=2):     (1) Claude/Fable 2026-08-26 契約審查；(2) 指揮明示採納並收緊 R2。
Reverse-test:       不把 R2 收成「新拿到的只是參數」。不刪 11.5a。不把 hunt_plan.py overlay 的 Phase 欄刪掉。
De-specified:       問題軸：同回合研究 vs 同回合使用新秘密；指揮面 vs 腳本 overlay。
Target-file:        SKILL.md R2／H2／§2／§6／§7／§9／frontmatter；execution-contract.md 11.5a；output-contract.md §9；stall-breaker.md
Consensus-tier:     中度（去重與可數化；R2 收緊使用／研究，未放寬使用秘密）
Status:             promoted
Subtraction:        刪 frontmatter／開頭／§6.1 對 H2 的複本；刪 §9 curl 複本；指揮列去掉 Phase 枚舉。
