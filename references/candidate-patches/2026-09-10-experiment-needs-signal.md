# Candidate Patch: 2026-09-10 — 實驗要有資訊量；迭代放能看見錯誤的地方

Trigger:            指揮不要照套 09-07 結構稿（打之前每格先答、SQL 殘段仍進 SKILL、地端優先寫成強制本地）。改成未來還用得上的模式。
Class:              mindset
Raw-observation:    Gavel：源碼已證實拼接、本機有 PHP＋MariaDB，卻對目標掃 31 發 payload；catch 把所有失敗收成同一空頁，被寫成 bet_killed。09-07 先補「註解家族／同一畫面」，指揮駁回為逐洞。同日結構稿把判別力寫成打前必答、把注入殘段留在 SKILL.md，會讓模型不敢探測、或把 SQL 當每條 primitive 的必掃清單。
Generalized-claim:  分不開的觀測不是實驗：成立與失敗對觀看者必須能分開，分不開＝未決，不得寫已測／已否證／已窮盡。允許少量探測去發現觀測已塌縮；禁止把塌縮上的家族掃完當成測過。本場已有源碼／binary 且片段已能在錯誤可讀的環境跑時，輸入家族在那裡展開，目標只收倖存者確認；沒有現成環境不要停下來搭實驗室。文章 payload 是假設來源。周圍環境（注入／解析點後面還有什麼、怎樣終結、錯誤被收成什麼）是環境維度，不是符號清單。
Sightings(n=1):     (1) Gavel PDO 欄位名注（2026-09-07）。獨立第二場仍缺；本卡以指揮明示「不要照套、改成你覺得有幫助的模式」授權，非 n 門檻達標。
Reverse-test:       不會害事：不禁止時間／長度等本身可區分的盲技巧；不強制搭實驗室（閘在「已能跑且錯誤可讀」）；本地命中不得冒充目標事實。會害事的讀法是「每格先答得出差異才准打」——那會擋住用來發現塌縮的少量探測，故不採用。
De-specified:       問題軸：實驗有沒有資訊量；迭代放在哪裡才看得到錯誤。不是「要用某條註解符」、不是「凡注入必本地」。
Target-file:        SKILL.md §2／§9；hunt-loop.md §4.1（§5 塌縮→unknown_primitive 保留）
Consensus-tier:     中度（心法；不碰 R1–R8、不縮攻擊面）
Status:             promoted（指揮 2026-09-10 明示改這條，不照套 09-07 稿）
Subtraction:        刪 SKILL.md 註解家族 gate、ORDER BY／語句形狀尾巴、Claim「同一畫面」尾巴。09-07 apply 腳本改拒絕執行。符號家族降為 hunt-loop illustration。不進 skill-craft 的「逐洞補丁」pitfall（那是改 skill 的元教訓，不幫下一場狩獵）。
