# Candidate Patch: 2026-08-28 — 本機 vantage（hosts）交給指揮

Trigger:            掃到 HTTP 轉址主名後，副駕駛用 Host 標頭當下一探，沒把加 `/etc/hosts` 的命令交給指揮
Class:              contract
Raw-observation:    nmap 顯示轉到 `gavel.htb`。HANDOFF 寫「不寫 hosts、用 Host 標頭對照」，把指揮排除在外。指揮明說要協作、他會先加 hosts，並要改 skill。
Generalized-claim:  目標已宣告、本機還解析不到的名字，是指揮的本機 vantage 活。下一步必須 `[USER]` 把加 hosts 的命令進 fence。禁止用只打 IP 或改 Host 標頭當「就不必請指揮」。Host／SNI 仍可測其他尚未宣告成主名的標籤。
Sightings(n=2):     (1) 本場開局掃完交 Host 標頭剩餘觀察、跳過 hosts；(2) 既有「寫 hosts = USER + fence」卻被讀成可選，指揮必須再點一次才加。
Reverse-test:       不會害事：指揮加完，瀏覽器與截圖走同一個名字。會害事的是把每個材料裡的短名都強制寫進 hosts——閘在「轉址／憑證／服務已宣告的主名」，不是凡 Host 必寫 hosts。指揮明示先不要改 hosts 時，Host 才當指紋。
De-specified:       問題軸：共享 vantage（本機解析／VPN／要指揮聽的埠）缺了，能不能用協定層變通跳過指揮？
Target-file:        SKILL.md §1；htb-preflight.md §2；hunt-loop.md §2.1；port-scan-pipeline.md §2.2；execution-contract.md §6；output-contract.md §1.3
Consensus-tier:     一般（互動偏好成規則；指揮明示改 skill）
Status:             promoted
Subtraction:        「再建議補 hosts」。把只打 IP／改 Host 當成合法下一探來跳過指揮。
