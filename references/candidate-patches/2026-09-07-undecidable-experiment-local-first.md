# Candidate Patch: 2026-09-07 — 無判別力實驗＋源碼在手卻不在地端展開

Trigger:            源碼已證實拼接注、本機可重現脆弱片段，卻直接對目標盲打 payload 家族；目標把所有失敗塌縮成同一畫面，打完把「全數同頁」寫成賭注關閉
Class:              mindset
Raw-observation:    Gavel inventory.php：31 發矩陣（8 種 sort 觸發 × payload 家族）全部與假欄位 zzzz 同 hash（catch{} 把 HY093／語法錯／未知欄塌縮成同一空頁），被寫成 bet_killed。工作站上有 PHP＋MariaDB、完整源碼、手法文示例，全程未做任何本地重現。指揮給出殘段註解正確的 payload 後一發命中。同日先前的 skill 修改（註解家族 gate、模板禁令、塌縮禁 kill）被指揮定性為逐洞補丁並駁回。
Generalized-claim:  實驗必須有判別力才是實驗：對目標開驗證矩陣前，逐格寫出「成立 vs 失敗」的可觀測差異；分不出來 → 該格未決，該批禁止下「已測／已否證／已窮盡」結論，先換能分開的 oracle（side channel、本地重現、或先造一個成立必然改變畫面的格子）。源碼在手且片段可本地重現時，payload 家族在地端展開迭代（吞錯的 catch 拿掉、語句環境每一軸掃全），目標只收倖存者確認；目標不是開發迭代場，盲打湊樣本不算測過。
Sightings(n=1):     (1) Gavel PDO 欄位名注（2026-09-07，31 發全同頁被寫成關閉；正確尾巴一發命中）。獨立第二場目擊仍缺；本卡以指揮明示授權升級，非 n 門檻達標。
Reverse-test:       不會害事：不禁止盲技巧——時間／長度 side channel 本身就是可區分觀測，閘在「答不出差異」不在「沒有畫面差」；不強制本地——條件是「源碼在手且可重現」；目標確認義務仍在，本地結果不冒充目標事實（版本差異要標明，parser 行為隨版本變）。
De-specified:       問題軸：實驗資訊量（判別力）與開發場域選擇（地端 vs 目標）。不含任何具體注入手法；終結符／殘段只當 illustration。
Target-file:        SKILL.md §2（一條 subsume）；hunt-loop.md §4.1（第 3 項回復原句＋新增第 4、5 項）；skill-craft.md §6（一條 pitfall）
Consensus-tier:     中度（問題軸＋情境層 ref；不碰 R1–R8、不碰契約層、不縮攻擊面）
Status:             superseded（2026-09-10-experiment-needs-signal — 指揮不要照套本卡／apply 腳本；判別力改「分不開＝未決」且允許少量探測，地端改「錯誤已可讀才迭代、不搭實驗室」）
Subtraction:        刪 SKILL.md 三條 09-07 增補句（外部材料／偵查矩陣／Claim 的加粗尾巴）與 hunt-loop §4.1 舊第 4 項；「註解／終結符家族」從 gate 降為 §4.1 illustration；「模板禁令」獨立句併入地端優先。淨行數約持平。