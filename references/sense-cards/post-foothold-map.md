# post-foothold-map

> **繁中**：立足後地圖：foothold 後要先釐清的面與證據（方法；無 PoC）。



## 何時用

- 已有**本場**低權會話／觀看者身份（foothold 已確認），要做「站穩後地圖」而非立刻升級。
- 從 foothold 切入 post-foothold 列舉：本機／域內可見物件、控制關係、秘密材料、群組與 ACL **類別**。

## 要驗證什麼

1. 身份與權級是否已寫入戰情（whoami／群組摘要／uid 類觀測）——缺則回 foothold，不開本卡。
2. 本輪列舉是否只產出**可複核事實**（路徑存在、ACE 類別、可讀設定、SUID／capability **標籤**），而非利用構想。
3. 每個有趣發現是否附：`finding class` + `verified|unknown` + `dead_if`；未知不得當門已開。

## 證據長什麼樣

最低門檻（缺一不可標「地圖完成」）：

| 元件 | 合格例子（抽象） |
|---|---|
| 觀看者 | 使用者名／uid／主要群組已觀測 |
| 剩餘觀察 batch | 至少一輪：本機檔案權限面／定時任務面／服務帳號面／目錄物件面（依 OS 選） |
| 發現表 | 每列：class｜fact｜verified｜禁止下一步（若有） |
| 負向 | 明確寫「未見」的類別（例：sudo 無、unconstrained delegation 未見） |

不合格：只有「感覺可以提權」；只有 CVE 號無本場指紋；把 SPN／SUID **類別**直接寫成「已可拿權」。

## 死路怎麼標

- 列舉兩輪零新物件且身份未變 → `DEAD:hypothesis-mismatch`，改假設或換面，不升 privilege 門。
- 需要高權才讀得到的面却無替代來源 → `DEAD:no-identity`（或標 unknown，禁止腦補）。
- 想跳過地圖直接提案利用級動作 → 拒；改標 `GAP:no-local-playbook` 若本地無方法卡。

## 去哪查

- 本庫：`evidence-gate`、`local-sense-memory`、`dead-path-mark`、`priv-esc-evidence-gate`。
- 公開：作業系統／目錄服務**概念**文件（權限模型、委派語意）——查法見 `public-doc-cve-lookup`。
- **禁止**：payload、PoC、逐步提權菜譜、票據／hash 攻擊指令、writeup。
