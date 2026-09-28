# dead-path-mark

> **繁中**：死路標註：何時把假設標死、避免重複撞牆（方法門；無利用步驟）。



## 何時用

- 假設落空、範圍越權、資訊面耗盡、或證據門長期不開時。
- 收尾與交接：讓下一手（人或 bot）不要重複撞牆。

## 要驗證什麼

1. 這條路是「暫時未知」還是「已證不可行／不該做」？
2. 標記是否攜帶：**關閉原因、保留的觀測、下次可重開的條件**（若有）。
3. 是否誤把「我不會」標成死路（應標 `GAP:skill-or-source`，屬知識缺口）。

## 證據長什麼樣

建議固定前綴（寫進戰情／筆記即可）：

| 標記 | 含義 |
|---|---|
| `DEAD:auth-boundary` | 超出授權，永久停 |
| `DEAD:http-thin` | Web 資訊面過薄，改其他面 |
| `DEAD:no-identity` | 無合法身分來源，禁升級域內動作 |
| `DEAD:hypothesis-mismatch` | 假設與觀測矛盾 |
| `DEAD:no-consumer` | 動作面無消費者／無副作用證據 |
| `GAP:version-unknown` | 缺產品版本，不准瞎猜 CVE |
| `GAP:no-local-playbook` | 本地無卡可載，需補卡或公開查法，不硬猜 |
| `DEAD:doctrine-incompatible` | 禁 PoC 編制下無 misconfig 可續面（見 doctrine-compatible-privesc） |
| `DEAD:platform-deny` | 面相容但指揮／平台拒批利用類動作（勿與上列混稱） |
| `DEAD:no-session-path` | 公開盤齊但無合法身分路徑且未獲重建批 |
| `DEAD:auth-readonly-exhausted` | 認證後只讀耗盡，需另批窄目標 |
| `DEAD:methodology-breach` | 方法論破口（payload／PoC／writeup 當主源） |
| `DEAD:cve-version-mismatch` | CVE 命中但版本不合 |
| `DEAD:advisory-only` | 僅有公告、無授權／無驗證計畫 |

每筆至少一行：`標記｜關閉的假設｜關鍵觀測｜重開條件或「不重開」`。

## 死路怎麼標

- 若連標記慣例都無法執行（戰情無處可寫）→ 先修狀態存放，不繼續擴假設樹。
- 禁止：用模糊句「好像不行」代替標記；禁止刪除觀測只留結論。

## 去哪查

- `evidence-gate`、`local-sense-memory`。
- 戰情狀態慣例：以 HuntSpear／warboard 欄位為準（本卡不規定 DB schema）。

> 紅線：無 payload／PoC／逐步利用。
