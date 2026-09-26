# Error Recovery — 通用錯誤恢復

當工具失敗、空結果、timeout 或非預期輸出時載入。

## 核心原則

**不要直接重試同一個命令。** 先診斷，再決定下一步。

## 分層診斷（由下而上）

**帶 error code/message 時最先做**：去識別搜尋是早期動作不是最後手段。在進入下面分層之前，先查 code 含義、已知原因、環境前提和現成解法——這通常比逐層排除更快定位。

1. 網路層：目標可達？VPN／tunnel？DNS？
2. 服務層：port 仍在聽？服務是否被打掛或重啟？
3. 認證層：憑證／ticket／token 是否仍有效？是否觸發 lockout？
4. 工具層：安裝與版本？語法是否適用此版本？實際送出的 request 是否被 client 改寫？
5. 環境層：container、proxy、SELinux、時鐘偏移？
6. GUI 層：畫面是否有 credential／錯誤提示？是否有更短的 GUI 路徑？未登入畫面先截圖（`hunt-loop.md` §2.3）。若下一觀測是要人點選／登入，HANDOFF 用 `[UI]`（`execution-contract.md` §6），不要再換一條 CLI 皮。
7. 知識層（無 error code 時）：這個失敗是否對應已知問題或未查到的前置條件？（去識別後搜尋；若上方已查可跳過）

## 失敗分類

| 類型 | 處置 |
|---|---|
| transient | 最多重試一次 |
| tool／syntax | 修正版本或參數，不改假設 |
| missing prerequisite | 暫停假設，查依賴 |
| hypothesis falsified | 關閉／暫停，記錄 scoped reopen-if |
| valid test／no signal | 檢查表示軸是否已測；未測則做表示差分 |
| representation untested | 不得宣告 primitive 耗盡 |

半成功時先命名「已成功層」與「缺口」，再規劃下一步。
