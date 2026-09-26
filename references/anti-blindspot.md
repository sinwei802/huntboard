# Anti-Blindspot Contract — 反覆蓋幻覺與未知 Primitive

需要處理不熟技術、清單外訊號、STALL／Goal Stuck，或自覺「references 沒寫到所以沒路」時載入。  
本文件優先於各 route 檔中的**示例表／階段序／具名手法**。

## 1. 核心命題

- Route references 是 **問題生成器與正交軸**，不是閉合招式百科。戰術內容每次用搜尋展開（`tactical-search.md`），不從本檔背。
- **未寫進 skill 的技術預設可能存在**；不得因「表上沒有」而降低先驗或直接排除。
- 具名手法（工具名、CVE 暱稱、ESC 編號、經典攻擊名）若出現在任何 reference，一律視為 **optional illustration（可選示例）**，不是 checklist gate。
- 完整感是 bug：越長的表越容易造成 coverage illusion。

## 2. Unknown-Primitive Protocol（硬流程）

當出現以下任一情況，進入本協議（可與 STEP 疊加，不授權自動利用）：

- 不熟的產品、協定、錯誤字串、控制面、服務角色
- 版本／build 已釘死但 skill／記憶中無對應手法
- 觀察到的能力無法映射到任何熟悉 technique 名稱
- 連續同構手法失敗，懷疑「不是招式問題而是模型問題」
- **看起來很熟**（常見 port／服務外形、經典 lab 題型）但 **尚未**對該 `product|role + version(若有)` 做過至少 1 條 **behavior／primitive lens** 查證或顯式 NAMING
- 新錯誤字串、新 build、或第 1 次手法 fail 後仍打算直接上「記憶中的下一招」

### 步驟（作業脈絡完成；每步可 HANDOFF）

1. **NAMING（抽象，禁止工具名當 Goal）**  
   用能力語言寫 primitive：  
   `誰（主體）— 對什麼物件 — 能造成什麼可觀測效果 — 在什麼通道／表示下`  
   例：`低權進程 → 觸發 root 代執行安裝交易 → 寫入系統路徑`  
   禁止：`用某工具打某洞` 當唯一 Goal 名。

2. **SLOT FILL（只填觀察到的）**  
   ```text
   product/control-plane | version/build | primitive | effect-wanted
   channel/representation | identity | trust-boundary | adjacent-systems
   failed-assumption | exact-error (redacted)
   ```
   未知留空，不猜。

3. **LENS SEARCH（先研究，不先套近義舊招）**  
   依 `tactical-search.md`／`search-mindset.md` 組最多 3 條正交 lens query（STALL 最多 5）。  
   **禁止**的第一步：把未知 primitive 硬映射成表內最像的經典招再執行。  
   允許：用示例名當 *search keyword 之一*，但必須同時有「行為／效果」lens。

4. **SYNTHESIZE**  
   結論只保留：前提、適用版本、否證條件、最小驗證實驗、1–2 來源。  
   寫入 search cache；標 `reopen-if`。

5. **MIN-TEST**  
   設計**一個**最小可觀測 STEP 驗證 primitive 或前提，不是完整 exploit chain。  
   Approval 規則不變。

6. **INTEGRATE OR DROP**  
   - 成立：新 `H-*`，claim scope = 已測通道×表示×操作  
   - 不成立：scoped 否定 + reopen-if；**不要**寫成「整類技術不存在」

## 2.1 看似熟悉仍要過門

熟悉外形是**最高頻盲點來源**（訓練語料 = 隱形過期 playbook）。

**觸發條件**：枚舉階段發現任何可識別產品或管理介面時，在「放棄該攻擊面」或「標記為低優先」之前，必須先過門。被認證擋住（403/auth fail）就放棄是此條最常見的違反模式——認證被擋不代表產品本身沒有可利用漏洞。

**過門要求**：對該產品 + 版本至少做過 1 次 CVE / exploit 搜尋（NVD 或 GitHub），確認是否有已知可利用漏洞。未搜尋就放棄 = 違規。具名產品（WAC、Jenkins 等）僅為 illustration，判準看「是否為可識別產品且未查證」，不列舉特定產品。

在對「很像 SMB／Apache／AD／sudo」的目標發出 **exploit／深度利用變體** 的 Target STEP 前，作業脈絡必須已有其一：

1. 對該 SUBJECT(+VERSION) 的 NAMING（能力語言 primitive），或  
2. cache 中至少 1 條 behavior／primitive lens 結論（含負面 + reopen-if）

否則下一步必須是 **Research STEP**（填槽 + ≤3 query 或讀可及 source），不是經典招。  
枚舉／版本指紋／讀材料不受此門阻擋。把二進位標成 stock／wrapper／apphost 仍要對載入／搜尋行為做 NAMING 或 lens；標籤不是關閉。

### 2.2 「我自己寫一個就好了」是同一個盲點

同樣的盲點也適用於「動手做」而不只是「判斷有沒有路」。「我自己寫一個就好了」感覺高效，但通用能力——parse 已知格式、說某個協定或 API、retry/backoff 迴圈、encode/decode、標準演算法——幾乎都已經被封裝成現成工具。手寫之前，花一個 query 搜尋是否已有維護中的工具或函式庫覆蓋這個能力；現成工具勝過你得從頭 debug 的手寫版本。這只適用於通用能力，不是目標特定的膠水邏輯——後者沒有現成對應物，不需要搜。

## 3. 反清單規則（任何 route）

| 禁止 | 改做 |
|------|------|
| 「表上沒有所以不是主線」 | 用正交軸生成 H；表外 H 至少留一條 active 或 untested |
| 把階段 A→E 當必須閘門 | 階段序 = heuristic；有高信心證據可跳，**表外邊不得自動墊底** |
| Goal = 工具／CVE 暱稱 | Goal = 概念能力（能力語言，見態勢列 Goal） |
| 只搜 technique 專名 | 先搜 product+version+behavior+effect |
| 記憶中的「這權只能做 X」 | 鉚版本後查當前 abuse surface |
| 帳號價值＝權限高低 | 帳號價值＝權限 × 資產 × 信任邊界；低權帳號可能存取獨有檔案、郵件、憑證、瀏覽器密碼等資產，橫向移動的目的是資產發現而非僅權限提升 |
| 繼承 BLOCKED 無 scoped 反證 | 重驗 primitive（error-recovery） |

## 4. 假設生成（不靠 playbook）

每個決策點至少嘗試產出 **3 條正交 H**（可與 Breadth Pass 合併）：

1. **直接面**：當前 Route 上，版本／設定／輸入／錯誤暗示的行為  
2. **身份／信任**：誰信誰、材料能否跨面、控制面是誰  
3. **相鄰／表外**：integration、source、artifact、另一 Route，或 **明確標 `[wildcard]` 的清單外角度**

   第三條若只是同一 payload 換皮，不算正交。
   `[wildcard]` 的價值就是逼出 skill 沒寫的方向。
   讀完第一份到手材料後，若未認證正交面仍未點名，不得把該材料暗示的利用當唯一主線（`hunt-loop.md` §2.2）。

   - **資產軸（常被遺漏的正交維度）**：目標帳號即使權限低，仍可能存取獨有的檔案、郵件、憑證、瀏覽器密碼、SSH key、設定檔等資產。橫向移動到不同帳號的核心目的之一是**資產發現**，不只是權限提升。每個帳號的資產存取面構成獨立的正交假設軸。判準：如果判斷「拿到這個帳號沒用因為權限一樣低」，就踩了這個盲點——先問「這個帳號能存取什麼目前看不到的資產」再做判斷。

   - **「已窮盡」是禁語（可機械判定）**：對一個 identity 的攻擊面，禁止在任何時候宣告「已窮盡」「無路」「到頂」。這些是不可機械判定的判斷——弱模型查了 2 個面就會宣告窮盡。改為：每次列舉已測面 + 未測面，未測面非空就不准宣告窮盡。已測面 = 本回合對該 identity 實際發出過查詢並拿到結果的面；未測面 = 尚未查詢的面（用資產軸推導，不列固定清單）。

## 5. 示例的合法用法

- ✅ 「例如歷史上常見 Kerberoast；**先確認是否有 SPN 與可達 KDC，再搜當前手法**」  
- ✅ 用示例當 search seed 之一  
- ❌ 「先做完表上所有項才准搜新東西」  
- ❌ 「沒看到 ESC 編號就當 ADCS 無路」  
- ❌ 把 pivot menu 當唯一決策樹

## 6. 與 STALL / Goal Stuck 的銜接

- Route STALL：未測軸 → 表示差分；軸盡 → Lens Search（本協議）  
- Goal Stuck（attempts≥3）：禁止同構；進入本協議步驟 1–5 或改 Goal  
- 研究 pass 仍受 3／5 query 預算與隱私規則約束

## 7. 對使用者的口語

進入本協議時用一兩句說明：

> 這塊我不該用內建清單硬套；我先把能力抽象成 primitive，查當前公開行為與前提，再給一個最小驗證。

不要說「skill 沒寫所以做不了」。
