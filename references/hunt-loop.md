# Hunt Loop — 觀察 → 展開戰術 → 依計畫打 → 回饋調整

戰役層。每則訊息仍受 SKILL 頂部 R1–R8 約束：一刀、停等、新發現不是授權。  
**HANDOFF 結束的是這個方向，不是這場狩獵。** 計畫帶到下一則，直到 engagement 成功（flag／root／報告）或指揮收工。

欄位、相位、開局意圖、可否深打：以 `scripts/hunt_plan.py` 為機械真源；持久化以 `scripts/warboard.py` 為準。改計畫後把同等欄位寫進 facts JSON，跑：

```bash
python3 "$SKILL_ROOT/scripts/warboard.py" apply --facts <檔>
python3 "$SKILL_ROOT/scripts/warboard.py" brief
```

作業脈絡沒有 sqlite 時，開局 `warboard.py opening` 會建空庫。checkpoint 才 `apply`。禁止把 `hunt-plan.md` 當本期前提。

---

## 1. 相位

```text
OBSERVE → DESIGN → EXECUTE ⇄ ADJUST →（Goal 達成則下一能力 Goal 回 DESIGN）→ SUCCESS
```

| 相位 | 獵人在做什麼 | 准許的目標動作 |
|------|----------------|----------------|
| OBSERVE | 看獵物：命名正交未認證面、讀手上材料、寫 HAVE | 淺：observe／fingerprint／read_local |
| DESIGN | 用**即時搜尋**把觀測展開成 2–3 條正交賭注與下一探 | 0 次目標 ACT（純研究） |
| EXECUTE | 打計畫上那一探 | 深打僅當 `allows-deep` 為 yes |
| ADJUST | 對比預期／觀測，改寫下一探 | 本回合不連打；交出改過的計畫 |
| SUCCESS | engagement 目標已達成 | 0；收尾走 §10 |

禁止：觀察未完就深打（H1）；未搜尋展開就深打（H2）；打完不改計畫（H3）；新事實不先補上一刀缺口就換執行者，或既有行程缺名未觀測就換執行者／覆寫主邏輯（H4）；把第一份材料暗示的利用當唯一下一刀；新觀看者未做剩餘觀察就沿第一份檔深挖。

---

## 2. OBSERVE — 先看獵物

觀察「夠了」= `hunt_plan.observation_complete`：HAVE 非空，四個面都是 `seen` 或 `oos`，手上材料不是 `unread`。

| 面（`SURFACE_CLASSES`） | 問的是什麼（不列埠／工具當閘） |
|-------------------------|----------------------------------|
| `transport` | 傳輸／listener 取樣了沒 |
| `identity_unauth` | 未認證身份面（匿名／guest／null／未登入目錄或 API）點名了沒 |
| `naming` | 名字／vhost／SAN／別名點名了沒 |
| `materials` | 已到手的每一類材料讀完或明示延後了沒（反編譯一份托管碼不算已讀同目錄原生 stub／config／第二個組件；標成 stock／wrapper／apphost 不算已觀察載入／搜尋行為；會渲染的網頁未截圖不算讀完，見 §2.3） |

`oos` 必須寫從哪個 identity、哪個 scope 看的。未看就標 oos = 過早關閉。

### 2.1 開局口語

`hunt_plan.py opening "<使用者原文>"`：

| 意圖 | 何時 | 授權的是什麼 |
|------|------|----------------|
| `observe_transport` | 開局／掃，且埠面未知 | 只做傳輸面 pipeline（見 `port-scan-pipeline.md`）。掃完 **STOP**。若出現本機還解析不到的已宣告名字：下一步先是 `[USER]` 加 hosts（`htb-preflight.md` §2），剩餘觀察寫在指揮加完之後。否則具名剩餘觀察 batch。 |
| `observe_remainder_batch` | 開局／掃，埠面已知，觀察未完 | 事前列名、互不依賴的未認證取樣：身份面 + 命名 + 取回可讀材料。禁止同批用掃到的結果去 exploit／登入。新觀看者的剩餘觀察見 §2.4（不是 opening 詞）。 |
| `named_step` | 其他 | 走 R3：只確認緊接在前的那一刀。 |

「掃／開局／進行作戰」**不是** rustscan 專用詞，也**不是**整場殺傷鏈通行證。  
新 listener 是新面：埠從掃描才知道 → 傳輸面掃完必須停。有未解析主名時，指揮加 hosts 回「繼續」= 確認你剛列名的剩餘觀察方向。禁止先交 Host 標頭剩餘觀察來跳過指揮。

### 2.2 材料不是殺傷鏈

「已在手」= 本 engagement 的 `./pentest-state/` 與指揮丟來的檔。舊案、其他目錄、整個磁碟不是。大檔先 grep／摘要；把 JS bundle／dump-dom／源碼樹整份灌進對話不算讀完。即將當成執行者去濫用的目標 binary／wrapper，它所 load 的 parser／源碼算手上材料；入口腳本本身不算已讀。

讀完第一份到手材料之後，若仍有未測的未認證正交面或新觀看者資產面（§2.4），下一探必須點名那些面（或一份預先列名的寬度 batch）。禁止把該材料暗示的 exploit／投遞測試寫成**唯一**下一刀。逃脫：未測正交面已空，或材料本身已是完整憑證 + 明確登入口（登入仍受 R2／R4）。

同一物件被兩個以上元件碰時，先交代每道門檢查的是什麼（檔名、魔術碼、身分、ACL、落地路徑、載入器查找的名字），再選下一探打哪一道。元件包含啟動該程式的 host／runtime／載入器，不只自訂 Main。寫入之後執行者鎖在既有行程、缺名用靜態分析或 host／loader 搜尋觀測：見 SKILL H4。沒有 Windows 執行環境不是關閉。門還沒交代就用同一 primitive 換路徑／檔名／投遞通道，算同軸空轉。

### 2.3 視覺網頁要截圖

會渲染的網頁／GUI（未登入第一眼、登入頁、錯誤頁、驗證碼、支付頁、後台）是材料，不是「之後再請指揮看」。

- ASSISTANT 用現成無頭瀏覽器截圖，存 `./pentest-state/loot/screenshots/`（檔名可讀：host-path 或等同）。
- 同時保存 HTML 或 dump-dom。curl／GET body 不算已看過畫面。
- 該面未截圖：`materials` 不得標 `read`（保持 `unread`，或指揮明示 `deferred`）。
- 檔案落地即完成觀察。HANDOFF 給路徑，禁止只寫「看起來是…」。圖是否進模型見 SKILL §7。
- 要點選、填表、MFA、原生憑證框才交 `[UI]`（`execution-contract.md` §6）。writeup 怎麼嵌圖由 writeup skill 品質契約管。

### 2.4 新觀看者剩餘觀察

開局 §2.1 的 `observe_remainder_batch` 只管未認證面。下列任一成立，也是新觀看者，H1 對**該觀看者**重開：

- HAVE 新出現一個 identity（帳號、行程 uid、已證實的 command execution）
- 信任邊界換了觀看者（RCE 成功、換成另一個已登入身份）

outcome 用 `new_surface`（或 Goal 達成後鑄下一能力 Goal）。下一方向必須是一份**事前列名、互不依賴**的剩餘觀察 batch，只問這個觀看者：

- 能讀到哪些秘密（含已有 Loot 對它能不能用）
- 有哪些獨有材料（它讀得到、上一觀看者讀不到的）
- 對他人有什麼控制關係

禁止把該觀看者碰到的第一份設定檔／第一個二進位暗示的利用寫成**唯一**下一探。11.5a 停的是「RCE 後順手枚舉」；它不授權把下一方向收成第一份檔的深挖。

逃脫：該觀看者的三問都已 `seen`／`oos`（oos 寫從哪個身份、哪個 scope），或材料本身已是完整憑證 + 明確登入口（登入仍受 R2／R4）。不列固定路徑或工具名；batch 從這個觀看者實際能碰到的東西列名。

---

## 3. DESIGN — 戰術即時展開，不寫死

觀察完成後、第一次深打前，必須做一次戰術展開。細節在 `tactical-search.md`。本檔只定戰役位置：

1. 用已觀測的產品／版本／primitive／錯誤當搜尋鍵（禁止先搜「分類體系叫什麼」）。HAVE 或已觀測服務裡有目錄／域身份／命名服務時，那些事實也是搜尋鍵——現場展開，不背手法表、不等 Stall。
2. 搜尋結果只用來**鑄賭注**：2–3 條正交假設，按「最便宜且能改 Goal 的一探」排序。最便宜看能不能改 Goal，不是看能不能留在已批准的動作類裡。未使用的秘密 × 已點名的其他身份／登入口，與權限升級同一類便宜探。排序第一若需要動作類升級或使用已有秘密，HANDOFF 把它寫成 `[CONFIRM-REQUIRED]` 選項；禁止改交排序第二的同權限變體、或只繼續解當前身份的下一把鑰匙。提出≠執行。HAVE 裡出現受約束執行者時，2–3 條裡必須有一條測剩餘參數能否蓋掉寫死的限制，不能只賭官方用法。
3. 寫 Hunt Plan：Goal（能力語言，禁止產品+CVE 當 Goal）+ 賭注 + `next_probe` + 每注的 expect／kill_if。賭注正交見 `hypothesis-engine.md`。
4. HANDOFF 交 2–3 條已排序選項（做什麼／預期／風險／停／為什麼現在），標建議；深打預設 `CONFIRM-REQUIRED`，除非當則已具名授權該探。格式見 `SKILL.md` §7。

**知道 Technique ≠ 授權。** 計畫改變下一方向的排序，不讓本則跨決策邊界。

OBSERVE 的目標結果剛回來、本則預算還有餘：允許在 INTERPRET 裡做這次 DESIGN 搜尋（研究，不是第二次目標 ACT）。其他「結果回來再搜」仍禁止。

Goal 達成後立刻鑄**下一個能力 Goal** 再 DESIGN，不要停下來等指揮發明戰役。engagement 成功才進 SUCCESS。

---

## 4. EXECUTE — 照計畫的那一探

下一刀必須是計畫上的 `next_probe`，或 H3 已寫明為何改探。  
T1 的 H／WHY-NEW 對應該注。通用能力先搜現成工具（R8）。  
深打前：`allows-deep` 必須能過（觀察完 + EXECUTE／ADJUST + Goal + 活躍賭注 + next_probe）。

### 4.1 一條賭注的偵查是矩陣，不是現場試錯

`next_probe` 若是「這條 primitive 成不成立」，同一組 expect／kill_if 的變體是**一個方向的偵查**，不是一串請示。變體軸包括通道、編碼、argv、旗標、路徑、mode、API version。HTTP 的 query／Cookie／Header／PATHINFO 只是 illustration，不是唯一形。

碰目標前先寫矩陣：

1. 這一注真正會變的軸（想遠一點：擋明碼後編碼還算同一注；寫死限制後面還能接的參數也是）。
2. 對照組：正常值、基線、工具會摺路徑／正規化造成的假陽性。
3. 分類規則：每個格子預期什麼碼／body，怎樣算成立、怎樣算被擋、怎樣算工具假象。成立與失敗必須能分開；分不開＝這一格未決，不是成立也不是已否證。同一畫面／同一 hash 是典型形，不是唯一形。允許少量探測去發現觀測已塌縮；禁止把塌縮觀測上的家族掃完當成矩陣做完。
4. 外部手法假設了注入／解析點的周圍環境（後面還有什麼、怎樣終結、錯誤被收成什麼）。那些假設在本場是否成立，是獨立軸；只變同一篇 PoC 的編碼／跳脫不算放大。具名符號家族（如註解符）是 illustration，不是每條 primitive 的必掃清單。
5. 本場已有可跑片段、錯誤已可讀 → 家族迭代放那裡，目標只收倖存者確認。本地命中不等於目標命中。沒有現成重現環境，不為這條去搭實驗室。

然後用腳本（或同方向一批呼叫）一次跑完，表寫進 `./pentest-state/loot/`，**矩陣跑完才 HANDOFF**。禁止每打一格就停下來問「繼續」。  
R8：多通道／多編碼的指紋是通用能力，先搜現成掃描器；沒有再手寫膠水。腳本預設停在檢測分類；寫馬／登入除非方向已點名。  
R5 仍管「同一格 × 同一 error 連打」；未跑完的格子不是換皮，是矩陣還沒做完。

---

## 5. ADJUST — 每刀都改計畫

目標結果一回來（成功或失敗）先填：

```text
預期：<這一探的 expect>
觀測：<實際看到>
outcome：fact_gained | bet_killed | new_surface | unknown_primitive | goal_achieved | engagement_done
```

expect 裡任何可觀測項沒看到：不得把該注寫成已證實。成功路徑少一步（該刪沒刪、該回沒回）時 outcome 不得是 `goal_achieved`；最多 `fact_gained` 並在觀測寫「缺 …」。  
`kill_if` 的可觀測項若與「對照失敗」無法區分（同一 status／同一空頁／同一 hash）：outcome 不得是 `bet_killed`，寫 `unknown_primitive` 或 stay，並換能分開這兩類的 oracle。

再用 `apply_adjust` 的同一套規則改寫相位／下一探（可跑 script，或手寫同等轉換）：

| outcome | 下一相位 | 調整 |
|---------|----------|------|
| fact_gained | EXECUTE | stay（attempts 歸零，同一注吃新事實） |
| bet_killed | EXECUTE 或 ADJUST | 有**真正正交**的下一注 → next-bet；否則 stall／回 DESIGN |
| new_surface | OBSERVE | re-observe |
| unknown_primitive | DESIGN | re-design |
| goal_achieved | DESIGN | re-design（新能力 Goal） |
| engagement_done | SUCCESS | success |

`bet_killed` 之後：若清單裡下一注只是同一產品的姊妹洞或剛關手法的換皮，視同沒有下一注——回 DESIGN 用能力 Goal 重鑄，或把身份／寫入面升級寫成 `[CONFIRM-REQUIRED]`。禁止「矩陣剛關就再寫一支同產品掃描」。

Stall 見 `stall-breaker.md`：先問觀察是否未完、計畫是否還有未測注；都沒有才做 Stall 戰術搜尋。

---

## 6. 與 STEP 的關係

- 計畫是跨則戰役記憶，**不是**跨方向通行證。
- 指揮確認 HANDOFF 裡標為建議的那一條（含「繼續」）= 打完那個方向，然後再 ADJUST。點名其他選項才換刀。
- 狩獵成功之前，每一則 Hunt HANDOFF 都必須帶可解析的狩獵態勢列與 2–3 條選項（`output-contract.md`）。checkpoint 只交態勢。
