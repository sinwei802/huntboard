# Local Sense — 方法／證據門薄層（非手法 cookbook）

> 載入時機：準備向指揮提案「下一刀／下一方向」之前（含 HANDOFF 選項成形時）。開局純 OBSERVE 指紋不必載。
> 目的：補上「會搜但沒 sense」——本地回答**該不該打、打哪、怎樣算打過**；雲端搜尋仍負責「可能怎麼打」。
> 紅線：本檔與 sense-cards **禁止** payload、PoC、逐步利用、可照做攻擊鏈。

## 0. 與「禁止 Route playbook」的切開

| 允許（本層） | 禁止（仍成立） |
|---|---|
| 相位、假設→證據門、死路標記、公開文件／CVE **查法** | 依 Route 堆手法步驟／利用菜譜 |
| 薄方法卡（何時用／驗證什麼／證據長什麼樣） | 把 CyberStrike 或 writeup 解法搬進 skill |
| 提案前強制對卡 | 用模型記憶冒充已過證據門 |

`SKILL.md` §4「禁止為 Route 建立 playbook」指的是**手法庫存**；本層是**決策 sense**，兩者不衝突。

## 1. 強制程序（可機械檢查）

提案任一新方向／下一探之前，助理必須在內部（或呼叫 `scripts/sense_gate.py`）備妥：

1. **phase**：orient｜map｜probe｜decide｜idle（對齊 warboard focus 語意即可）
2. **hypothesis**：可證偽的一句話
3. **evidence_gate**：已觀測到什麼才算門開（具體、可複核；禁止「感覺像」）
4. **dead_if**：什麼觀測會標死路／關閉假設
5. **card_id**：對到的薄卡短名（見 §2）；無卡可對 → `GAP:no-local-playbook`，只能提案「蒐證／查雲端源」，不得提案利用級動作類
6. **cloud_cross**：至少引用 `cloud-sources.md` 裡 **2 個** active 源 id（如 `src-nvd`、`src-websearch`）（查詢鍵來自指紋，不是 writeup）

缺任一項 → **不得**輸出帶利用／auth_use／spray／pivot 類的建議選項；只准 OBSERVE／Research／或 `challenge-board-handoff` 類**具名可稽核下一階** HANDOFF（仍標 CONFIRM；禁止菜譜正文）。

## 2. 內建薄卡（短名）

卡全文在 `references/sense-cards/`。Vault 鏡像：`資安/HuntSpear 薄 playbook/`（LiveSync；以本 skill 樹為 runtime 真源，vault 供人讀與雙軌例行改善）。

| card_id | 檔 | 何時用 |
|---|---|---|
| `http-observe-only` | `sense-cards/http-observe-only.md` | Web／HTTP 面初勘 |
| `evidence-gate` | `sense-cards/evidence-gate.md` | 任何升級動作前 |
| `dead-path-mark` | `sense-cards/dead-path-mark.md` | 假設落空／越權／面耗盡 |
| `public-doc-cve-lookup` | `sense-cards/public-doc-cve-lookup.md` | 有產品／版本指紋要查 |
| `local-sense-memory` | `sense-cards/local-sense-memory.md` | 開場建戰情／回合收斂記什麼 |
| `post-foothold-map` | `sense-cards/post-foothold-map.md` | 站穩後本機／域內地圖列舉 |
| `priv-esc-evidence-gate` | `sense-cards/priv-esc-evidence-gate.md` | 提權相位證據門（無 exploit 步驟） |
| `web-app-evidence-ladder` | `sense-cards/web-app-evidence-ladder.md` | Web／訓練應用：公開盤→達標證據階梯 |
| `challenge-board-handoff` | `sense-cards/challenge-board-handoff.md` | 挑戰盤已見：強制可稽核下一階交班句式 |
| `session-break-rebuild` | `sense-cards/session-break-rebuild.md` | remount／重起後工作階段重建 checklist |
| `owner-root-flag-bar` | `sense-cards/owner-root-flag-bar.md` | 主人尺：只認 root flag；中間旗不計 |
| `doctrine-compatible-privesc` | `sense-cards/doctrine-compatible-privesc.md` | 提權是否與禁 PoC 編制相容 |
| `post-engagement-retro` | `sense-cards/post-engagement-retro.md` | 成敗結案後薄复盤（必做） |

## 3. 與搜尋預算的關係

- 戰術細節仍走即時搜尋（H2）；本層不替代搜尋。
- 搜尋命中若只有「菜譜步驟」→ 可作研究筆記，**不得**直接寫進提案指令；提案仍須過 §1 證據門。
- 無版本指紋時依 `public-doc-cve-lookup` 標 `GAP:version-unknown`，禁止瞎猜 CVE 利用。

## 4. 改善

週一「HuntSpear 知識雙軌維護」例行會改卡／廢卡／增雲端源。技能樹內卡變更寫入 `CHANGELOG.md`；禁止為交差堆手法卡。

## 5. Vault 對照

人讀鏡像與回寫規則見 `sense-vault-map.md`。戰鬥只認本樹卡片。
