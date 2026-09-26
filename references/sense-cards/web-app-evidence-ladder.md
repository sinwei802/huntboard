# web-app-evidence-ladder

> **繁中**：Web 證據階梯：公開 observe 後下一階要交什麼（方法；無解法）。


## 何時用

- Web／應用類 lab（含 scoreboard／challenge 盤）已做完公開 observe，要提案「下一階」時。
- 訓練／評測場：達標常是「可稽核的 admin／challenge 進展」，不是「掃完就收」。

## 要驗證什麼（階梯，缺階不跳）

1. **公開盤**：版本／路由／靜態資源／匿名 API 行為已入戰情（可複核）。
2. **身分面**：登入／註冊是否存在；若只指紋頁面＝仍停在公開盤，不算身分面通過。
3. **工作階段事實**：有狀態碼＋session／token／cookie 差異證據（只記事實，不寫負載）。
4. **認證後只讀對照**：anon vs auth 差異已記；仍無「目標達成證據」時，下一刀必須是**指揮另批的窄段**（例如單一可稽核目標），不是默認噴射。
5. **達標證據門**：admin 面板可達 **或** 某 challenge 完成——兩者皆需 request／response 或同等可稽核輸出入戰情。

## 不合格（門未開）

- 只有列名／指紋／一次良性註冊就宣稱「Web 段打完」。
- 把外部 writeup／challenge 名稱清單當本場證據。
- 未獲批就開利用級／噴射級動作。

## 死路怎麼標

- 公開盤齊、但無合法身分路徑且指揮未批重建 → `DEAD:no-session-path`（等批重註冊／重登，不硬猜）。
- 有 session、認證後只讀無新可證偽假設 → `DEAD:auth-readonly-exhausted`，HANDOFF 請批下一窄目標，不自開利用。

## 禁

- payload／PoC／逐步利用菜譜進本卡或戰情。

## 強制交班（防卡死在 observe）

公開盤＋（可選）身分／只讀對照完成後，**不得**再以「再觀察」當建議主選項。必須載入 `challenge-board-handoff`（若有挑戰／任務盤）或具名 HANDOFF：管理面只讀探達／挑戰向單階／session 重建。指揮未批＝停，不算達標。
