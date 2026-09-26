# Candidate Patch: 2026-08-14 — source-first 不是殺傷鏈授權

Trigger:            讀完第一份可讀材料後，下一步自動變成該材料暗示的利用路徑，指揮必須把副駕駛拉回寬度
Class:              mindset
Raw-observation:    開局只做了端口掃 + 匿名 FTP 取回。changelog／SampleScanner 一讀完，後續連續 STEP 都沿著 queue 可寫 → IIS /dev → DNS 名 往下鑽。指揮 intervening：「寬度枚舉夠嗎 你只做了FTP 然後就開始鑽了」。當時未測：389/445 實測、未認證 LDAP/SMB/Kerberos、RPC、vhost。後來補寬度才發現漏埠、CA web、以及真正的 dev vhost。
Generalized-claim:  source-first 只授權「讀手上材料」。讀完之後，若仍有未測的未認證正交面（身份／命名／其它傳輸），HANDOFF 的下一步必須點名那些面（或一份預先列名的寬度 batch），不得把該材料暗示的 exploit／投遞測試當唯一下一步。
Sightings(n=1):     本場 HTB 開局（FTP 材料 → 過早沿掃描器鑽）
Reverse-test:       不會害事：並不禁止之後測該材料的 exploit，只禁止在寬度未點名時把它當唯一主線。反例「材料已經是完整憑證＋明確登入口」仍應先讀完再決定，不強迫再掃無關面——可用「未測正交面為空」當逃脫。
De-specified:       問題軸：讀完第一份 source 之後，寬度與深挖誰先？
Target-file:        references/anti-blindspot.md 或 thinking-loop INTERPRET；若要可機械閘，才考慮 T 卡（重大）
Consensus-tier:     中度（心法）；若寫成硬閘則重大
Status:             promoted
Subtraction:        升級時刪／改「source-first 之後自然跟材料走」的暗示，避免被讀成殺傷鏈許可

四態：promoted（2026-08-16 收進 hunt-loop.md §2.2；指揮授權狩獵循環）
