# Tradecraft Index — 薄索引 + 症狀決策樹

這份是**心法層的門房**，不複製任何心法內容（守 `skill-craft.md` §1.6 去重）。
用途：當你不確定「現在該開哪一份 reference」時，先看這裡的決策樹，再去讀對應那份。

## 決策樹（症狀 → 開哪一份）

| 症狀／情境 | 開這份 | 為什麼 |
|-----------|--------|--------|
| 動作類升級／高風險 CONFIRM 卡（本 session 尚未讀過） | `execution-contract.md` | 授權、執行者、回合邊界；開局觀察不必讀 |
| 開局、觀察夠不夠、戰役相位、Hunt Plan | `hunt-loop.md` | OBSERVE→DESIGN→EXECUTE⇄ADJUST |
| 改 skill／除錯循環內部步驟 | `thinking-loop.md` | 十二步展開；戰鬥不必載；閘門仍以 SKILL 頂部為準 |
| 「reference 沒寫所以沒路」、清單外訊號、看似熟悉卻沒 lens 過 | `anti-blindspot.md` | 反覆蓋幻覺、未知 primitive 協議（**優先於任何示例表**） |
| 不知道怎麼設計一次搜尋、query 該怎麼組 | `search-mindset.md` | 一般搜尋心法與去識別 |
| 觀察完成、目錄／域身份進 HAVE、Goal 剛換、或 Stall 且賭注已盡 | `tactical-search.md` | 即時搜尋鑄／重鑄 Hunt Plan |
| 連續 3 步無新事實、卡住 | `stall-breaker.md` | Stall 診斷流程 |
| 假設組合怎麼維持正交、怎麼寫否證條件 | `hypothesis-engine.md` | 假設 portfolio 管理 |
| 工具空結果／錯誤／半成功 | `error-recovery.md` | 分層診斷，不直接重試同命令 |
| 要回報、Triage、態勢列／選項欄格式 | `output-contract.md` | 口語輸出與選項欄 |
| 要改欄位定義 | `state-schemas.md` | 狀態 schema；保存進度跑 `checkpoint_write.py` |
| HTB／lab 開局、VPN、`*.htb`、交 flag | `htb-preflight.md` | 開局連通與 preflight |
| 使用者說「掃／快掃／完整掃／存到 ./scan」 | `port-scan-pipeline.md` | depth × persist × 修飾三軸 |
| 收尾（root／flag／報告）或「記下這次」 | `learning-loop.md` | 學習回路六步（見 SKILL §10） |
| 要改本 skill 的紅線／閘門／HITL 措辭 | `skill-craft.md` | 弱模型適配工藝條 |
| 要討論「skill 文字擋不住 runtime 壓力」 | `p0-runtime-brief.md` | runtime backlog 與誠實邊界 |
| 準備提案下一刀／下一方向、證據門／死路／對卡 | `local-sense.md`（必要時 `sense-cards/<id>`） | 本地 sense：該不該打、打哪、怎樣算打過；跑 `sense_gate.py` |
| Web／scoreboard 已 observe、不知何時算達標／該請批哪一階 | `sense-cards/web-app-evidence-ladder.md` | 公開盤→身分→session→只讀對照→可稽核達標；禁菜譜 |
| 挑戰／任務盤已入 HAVE、卻只想再 observe | `sense-cards/challenge-board-handoff.md` | 強制可稽核下一階 HANDOFF 句式 |
| remount／重起／path-wipe 後舊 JWT・cookie 可疑 | `sense-cards/session-break-rebuild.md` | 先記斷裂、再批重建；失敗等重註冊授權 |
| 主人尺／中間旗會不會被誤報成達標 | `sense-cards/owner-root-flag-bar.md` | 只認 root.txt |
| 提權枚舉完只剩 CVE／PoC 路徑 | `sense-cards/doctrine-compatible-privesc.md` | 標不相容、HANDOFF 改靶／停火 |
| 場次結案（成或敗）要改 skill | `sense-cards/post-engagement-retro.md` | 失敗補洞＋成功复盤都做 |
| DESIGN／戰術搜尋要多源交叉、或 sense 要求 cloud_cross | `cloud-sources.md` | ≥2 active 雲端源；禁止單點模型記憶 |
| vault 薄卡與 sense-cards 是否同一句、要回寫哪邊 | `sense-vault-map.md` | 雙源對照；runtime 以 skill 樹為準 |

## 兩條分流硬規則

1. **看似熟悉是最高頻盲點**：常見 port／服務外形（SMB／Apache／AD／sudo…）在發 exploit 類 Target STEP 前，若沒有 NAMING 或 ≥1 條 behavior lens 結論，先開 `anti-blindspot.md` §2.1，不要直接套經典招。
2. **心法 ref 是問題生成器，不是招式表**：任何示例手法都是 optional illustration；「表上沒有」不等於「沒路」。

## 只讀一份原則

一次只讀最相關的一份心法 ref；跨主題時才加載第二份。避免每回合把整個 references/ 灌進 context——那會稀釋頂部紅線的可見度。
