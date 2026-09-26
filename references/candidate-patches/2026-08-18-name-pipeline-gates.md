# Candidate Patch: 2026-08-18 — 同物件多道門先點名再換路徑

Trigger:            兩個元件碰同一物件（上傳器寫入、掃描器讀取）時，副駕駛把其中一道門的失敗／成功直接當成整條鏈，並用同一 primitive 的路徑變體當連續下一刀
Class:              mindset
Raw-observation:    網站依上傳檔名留下 .exe、丟掉 .zip；掃描器依落地路徑 EndsWith(".zip") 才解壓。副駕駛未先畫這兩道門，就連續換 inetpub／app／覆寫 DLL，指揮說「矇著頭打」「沒有戰略思路」。
Generalized-claim:  同一物件被超過一個元件碰時，HANDOFF 的判斷必須先點名每道門檢查的是什麼（檔名／魔術碼／身分／ACL／落地路徑），再決定下一探打哪一道。禁止在門還沒點名時，把同一 primitive 的路徑／檔名變體當成唯一下一刀。
Sightings(n=2):     (1) 本場：網站副檔名門 vs 掃描器路徑門被合成「上傳 zip」；(2) 既有 2026-08-14 source-first-not-killchain：讀完材料就沿暗示利用連打，未點名未測正交面。
Reverse-test:       不會害事：多說一道門比連打變體便宜。反例「每個 HTTP 參數都先畫完整資料流圖才能打」才膨脹——閘在「已看到 ≥2 個元件碰同一物件」或「指揮問這功能怎麼運作」。
De-specified:       問題軸：多元件同物件時，先點名門還是先換利用變體？
Target-file:        hunt-loop.md §2.2 之後；SKILL.md §2 同軸空轉
Consensus-tier:     中度
Status:             promoted（指揮明示修正 skill；與已 promote 的 source-first-not-killchain 同軸，補「門」而不是再寫一條殺傷鏈禁令）
Subtraction:        不新增「必須畫攻擊鏈」空泛句；只在已有「材料不是殺傷鏈／同軸空轉」旁補門的點名義務
