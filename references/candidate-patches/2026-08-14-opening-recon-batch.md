# Candidate Patch: 2026-08-14 — 開局「掃」與指揮點頭密度

Trigger:            指揮開局說「進行作戰／先掃描」，之後每一個未認證偵察都要再點一次頭，指揮感覺自己介入過多
Class:              contract
Raw-observation:    第一則訊息具名的是掃描，port-scan-pipeline + htb-preflight 把它收成「只做傳輸面 pipeline，掃完 STOP」。其後 FTP、反編譯、queue STOR、IIS Host、DNS、漏埠、SMB、ffuf 各自一則「同意」。指揮後來明說「寬度枚舉 允許批次作業」，才一次補上身份／漏埠。指揮收尾檢討：太常介入，skill 不太完善。
Generalized-claim:  在 CTF／單機開局語境，口語「掃／開局／進行作戰＋先掃描」應能對應一份**預先寫死、互不依賴**的開局寬度 batch（傳輸面 + 未認證身份取樣 + 命名／vhost），而不是只授權 rustscan。這不放寬 R1 的「結果拿去打下一招」，只把開局取樣一次列名。
Sightings(n=1):     本場「先掃描」被收成僅端口，指揮多次 同意 才補到寬度
Reverse-test:       會害事的套用：把「掃」自動擴成對整段 CIDR 做 LDAP/SMB/vhost。必須把擴張鎖在「單主機／已列名目標 + 開局語境」。生產／脆弱環境若指揮只要端口，擴張也煩——所以這是模式預設，不是全域放寬 R1。
De-specified:       問題軸：開局「掃」的授權邊界是「傳輸面」還是「未認證取樣包」？
Target-file:        references/htb-preflight.md、references/port-scan-pipeline.md；動 R1 則拒（那是另一件事）
Consensus-tier:     中度（開局契約）；若改 R1 預設每則可多個目標 ACT → 重大且應拒絕
Status:             promoted
Subtraction:        若升級，改寫 htb-preflight「preflight 後必 STOP、禁止同輪端口掃」旁容易被讀成「開局永遠一次只准一種偵察」的句子；不要刪 R1

四態：promoted（2026-08-16 收進 hunt-loop.md §2.1；指揮授權狩獵循環）

## 與「介入過多」的誠實切分

- **設計內的介入**（應保留）：exploit、噴密碼、改狀態、用新發現的身份、對新 Host 做下一跳。
- **過密的介入**（本卡要處理）：同一個開局目標上，互不依賴的未認證列舉被拆成十次「同意」。
- **不是 R1 壞了**：指揮點名 ffuf／gobuster 仍應是具名動作；壞的是開局沒有一份一次授權的寬度清單，以及 source-first 被執行成單軸深挖（見姊妹卡）。
