# Candidate Patch: 2026-09-16 — 新觀看者剩餘觀察

Trigger:            新 identity／RCE 之後沿第一份到手材料深挖，指揮必須把副駕駛拉回寬度
Class:              mindset
Raw-observation:    Management：openam RCE 後讀 boot.json → 鑽 JCEKS／DM；/opt 有 glpi／backup／sysmon 未列名。指揮：「你沒有進行過枚舉」「/opt 裡面明明那麼多有趣的東西」。08-14 開局 FTP 第一份檔同樣往下鑽。
Generalized-claim:  開局剩餘觀察 batch 的同類閘適用於任何新觀看者。新 identity／新 command execution 進 HAVE 後，H1 對該觀看者重開；下一方向必須事前列名互不依賴的剩餘觀察（能讀的秘密、獨有材料、對他人的控制關係）。禁止把該觀看者碰到的第一份檔暗示的利用當唯一下一探。11.5a 停的是順手枚舉，不授權把下一方向收成第一份檔。
Sightings(n=2):     (1) 08-14 開局 FTP 材料 → 過早沿掃描器鑽。(2) Management foothold boot.json → 過早沿 keystore 鑽。
Reverse-test:       不會害事：不禁止之後測該材料的利用，只禁止寬度未點名時當唯一主線。不列固定路徑清單。逃脫＝該觀看者三問已 seen／oos，或材料已是完整憑證＋明確登入口（R2／R4 仍在）。
De-specified:       問題軸：新觀看者的寬度與第一份材料的深挖誰先？不是「foothold 必跑某工具」。
Target-file:        SKILL.md H1／§5；hunt-loop.md §2.4／§2.2；execution-contract.md §11.5a
Consensus-tier:     中度（心法；不碰 R1–R8）
Status:             promoted（指揮 2026-09-16 授權改 skill，保持心法）
Subtraction:        刪 SKILL「新 identity 是新資產面」空宣言。不新增路徑／工具清單。
