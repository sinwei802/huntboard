# Cloud Sources — 多源雲端登錄（skill 內建）

> 載入時機：DESIGN／戰術搜尋、或 sense 閘要求 `cloud_cross` 時。
> 契約：不進薄 playbook 的時效知識，必須靠**足夠且不只一個**的雲端源，並能主動增刪（見例行維護）。禁止單點依賴模型記憶或單一搜尋結果頁。

## Active 源（v1）

| id | 來源 | 用途 | 信任邊界 | 何時不用 |
|---|---|---|---|---|
| `src-nvd` | NVD／CVE Program | CVE、受影響產品／版本 | 官方索引 | 當利用步驟主源 |
| `src-vendor-adv` | 廠商 Security Advisory（依指紋選） | 補丁、官方受影響版本 | 須對上產品指紋 | 無指紋時亂點廠商 |
| `src-rfc-mdn` | RFC／MDN／官方協定文件 | 協定／HTTP 語意 | 標準與概念 | 當攻擊菜譜 |
| `src-cisa-kev` | CISA KEV | 已知被利用優先序訊號 | 優先序，非利用說明 | 當逐步 exploit |
| `src-websearch` | 通用網搜（多引擎交叉） | 發現 advisory／文件線索 | **必須**再交叉另一 active 源 | 單頁 SEO／解題文當唯一依據 |

## Watch

| id | 來源 | 註 |
|---|---|---|
| `src-attack-mitre` | MITRE ATT&CK | 高階技巧家族命名；不當逐步利用主源 |

## 增刪規則（執行者／例行）

**新增**：填補決策缺口 + 寫用途／信任邊界／何時不用 + 穩定公開 URL 或名稱。  
**Retired**：連續健康檢查失敗、廣告／惡意下載為主、或純 exploit cookbook 且無標準對照價值。  
**降级 watch**：不穩定或易混 writeup 劇透 → 不得單獨支撐下一刀。

人讀長表可對 vault：`資安/HuntSpear 薄 playbook/雲端資料來源登錄.md`。衝突時以**本檔 + CHANGELOG 較新條**為 runtime 準。
