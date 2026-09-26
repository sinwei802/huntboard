# Candidate Patch: 2026-08-18 — 部分觀測不是已證實

Trigger:            指揮問「你實驗過了嗎／你逆向過了嗎／SMB 權限測了嗎」時，副駕駛把讀過的程式、列過的 share、或缺一步的現場現象講成已證實
Class:              contract
Raw-observation:    反編譯 DLL 的 C# 後稱材料已讀；只 `ls` share 卻在敘事裡當權限盤點；zip 穿越後檔出現在兄弟目錄但 zip 未被刪（成功路徑應 Delete），仍對指揮說 Zip Slip「已實驗證實」。指揮用公開 Zip Slip 文打臉：那是脆弱寫法對得上，不是實驗做完。
Generalized-claim:  正向 claim（已證實／實驗過／已逆向完／已測某操作）的 scope 不得大於已看到的 expect 可觀測項。讀 source／advisory／Technique 名是研究。列出物件是存在性。對該物件做寫入／執行／覆寫是另一個操作。成功路徑少一步（該刪沒刪、該回沒回）＝未證實，只能寫「與假設相容，缺 …」。
Sightings(n=3):     (1) 同一場：稱 exe 已逆向，實為只讀托管 C#；(2) 同一場：稱 SMB 權限，實為只列目錄；(3) 同一場：稱 Zip Slip 已實驗證實，成功路徑的 Delete 未觀測且無對照組。三個是同一問題軸的三次發作，不是三場獨立 engagement；第二場目擊仍缺。
Reverse-test:       不會害事：只禁止把部分觀測升格，不禁止在證據夠時說已證實。反例「每次都要完美對照實驗才能往下打」才會癱瘓——閘在用語與 claim scope，不在禁止下一刀。
De-specified:       問題軸：正向 claim 的證據門檻（研究／列舉／實驗／完整成功路徑）
Target-file:        SKILL.md §2 Claim 不可膨脹；§9 禁止；output-contract.md §10；hunt-loop.md §5 ADJUST
Consensus-tier:     中度（強化既有 claim 原則，不新增 R 編號）
Status:             promoted（指揮明示修正 skill；中度措辭落入既有 Claim 欄位，未新增 R 編號。獨立 engagement 第二場目擊仍建議補記）
Subtraction:        刪／取代過窄的「Claim 不可膨脹：關閉必須寫明 scope」單句，改成關閉與正向證實共用同一套 scope 門檻，避免並列兩條同義原則
