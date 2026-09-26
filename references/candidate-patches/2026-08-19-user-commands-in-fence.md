Trigger:            指揮要改 skill 互動區塊：未來需要他執行的指令都必須包在 code fence
Class:              contract
Raw-observation:    表已經改成 markdown fence 才能複製。指揮接著要求：要他跑的指令同樣全部進 fence，不要散在句子裡。
Generalized-claim:  需要指揮自己執行的指令全部放進獨立 code fence；區塊內只有純命令。說明在區塊外。禁止散文或行內 backtick 當交付。這是輸出／互動偏好成規則。
Sightings(n=2):     (1) 掃完表必須用 fence 才能複製原文；(2) 指揮明示指令也要全部進 fence。
Reverse-test:       不會害事：ASSISTANT 自己跑的命令不必印給指揮。UI 步驟仍寫回傳欄位，不是假造一條命令。
De-specified:       問題軸：要人複製去跑的字串，用什麼表面交給指揮？
Target-file:        SKILL.md §7；output-contract.md §1.3；execution-contract.md §8
Consensus-tier:     一般（輸出偏好成規則；指揮明示改 skill）
Status:             promoted
Subtraction:        把命令只寫在散文或行內 backtick 當交付。
