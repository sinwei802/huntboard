# Candidate Patch: 2026-09-07 — 代入後殘段未重建就關注入注

Trigger:            源碼已證實「欄位名拼接 + 鄰項綁定」，外部手法文的 payload 矩陣全空，就把該注 scoped 關掉
Class:              mindset
Raw-observation:    外部 PDO emulate／欄位名誤綁手法文的示例句在 `WHERE col = ?` 結束，用 `#` 當註解。本機語句在 placeholder 後還有 ORDER BY；`#` 落在 backtick 識別名裡對 MySQL 不是註解。catch 把語法錯、未知欄、HY093 收成同一張空頁，與假欄位對照 hash 相同，被寫成 parser 沒觸發。指揮提供殘段用 `;--+` 的 payload 後同一 oracle 立刻回顯。GET／POST／參數順序不是成因。
Generalized-claim:  外部 PoC 的註解符綁的是作者那句 SQL 的形狀，不是本機語句。拼接／parser 誤讀的矩陣必須先寫出代入後完整語句（含注入點後殘段），並把註解／終結符家族當獨立軸。對照組與候選同一畫面時 kill_if 未決，禁止 `bet_killed`。
Sightings(n=1):     (1) 本場：空頁＝zzzz 被當成 PDO 注已關；正確殘段註解後成立。獨立第二場目擊仍缺。
Reverse-test:       不會害事：只禁止用塌縮 oracle 關閉、禁止把文章 payload 當模板；不禁止在能區分的 oracle 上否證。反例「每種註解符都要掃完才能往下」會膨脹——閘在「殘段未寫進矩陣／兩類失敗同一畫面」這兩件可數事，不在枚舉符號。
De-specified:       問題軸：外部手法的語句形狀假設；關閉所需的可區分觀測。不是「要用某條註解符」。
Target-file:        SKILL.md §2 外部材料／偵查矩陣／Claim；§9；hunt-loop.md §4.1、§5
Consensus-tier:     中度（強化既有三句，不新增 R 編號）
Status:             superseded（2026-09-10-experiment-needs-signal）
Restructured-by:    2026-09-10-experiment-needs-signal — 塌縮觀測未決與「文章不是模板」留下；註解家族／同一畫面／打前必答皆不採用。
Subtraction:        不新增第四條核心原則。外部材料句加上語句形狀；偵查矩陣加上終結符軸；Claim 加上塌縮畫面不得關閉。刪「只列通道／編碼就算矩陣做完」的暗示。
