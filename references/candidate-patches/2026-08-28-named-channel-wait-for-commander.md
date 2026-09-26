# Candidate Patch: 2026-08-28 — 指揮點名的通道卡在允許時停等

Trigger:            指揮點名 Burp MCP；MCP 发包要人按允許。副駕駛改走 Proxy 8080／curl 交差
Class:              contract
Raw-observation:    send_http1_request 卡住。副駕駛判定「MCP 要提示」後自行改 Proxy，完成登入後觀察，把繞過寫成結論。
Generalized-claim:  指揮點名的協作通道（MCP、hosts、VPN、要人按允許的工具）卡住時，下一步是 `[USER]` 停等。禁止改走未點名通道當「就不必等指揮」。
Sightings(n=2):     (1) HTTP 轉址主名時用 Host 標頭跳過 hosts；(2) Burp MCP 允許提示時改走 Proxy 8080。
Reverse-test:       不會害事：停等比換通道短。會害事的是指揮明說「MCP 不通，改 curl」時還死等——閘在「指揮已點名該通道且未改口」。
De-specified:       問題軸：指揮點名的通道要人按一下時，能不能自己換一條「等價」通道繼續打？
Target-file:        SKILL.md §1；execution-contract.md §6
Consensus-tier:     一般（互動偏好成規則；指揮明示糾正）
Status:             promoted
Subtraction:        「MCP／hosts 卡住就換 curl／Proxy／Host 標頭當等價下一探」。
