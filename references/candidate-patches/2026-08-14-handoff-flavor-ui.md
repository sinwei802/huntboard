# Candidate Patch: 2026-08-14 — 交回要有「該人做」的味道

Trigger:            指揮覺得 huntboard 不像 redthread：沒有「這時候該把畫面交回來」的停點，只有「同意下一條 CLI」
Class:              contract
Raw-observation:    本場 HANDOFF 幾乎全是 `[ASSISTANT | CONFIRM-REQUIRED]`：掃完、FTP 完、LDAP 完、gobuster 完都等同意再跑下一條命令。IIS `/certsrv` 401 NTLM、以及後來的 `Host: dev.bruno.vl` 200，下一步仍被寫成 assistant GET，沒有變成 `[UI]`（開瀏覽器、看頁、回傳標題／表單／錯誤）。huntboard 的 UI 段被壓成兩句；redthread 是獨立 §4，且主檔寫「UI 也是 attack surface」。
Generalized-claim:  HANDOFF 有兩種味道，不能共用一種停法。（1）授權用盡：R1，動作做完就停，下一步仍可以是 CLI。（2）能力在人：下一觀測是看畫面、登入、MFA、點選、比對視覺／JS 渲染，executor 必須是 `UI`（或 `USER`），並寫回去哪裡、做什麼、回傳哪些欄位／截圖。只做（1）會變成點頭機；該做（2）卻繼續 curl，會漏掉渲染與憑證面。
Sightings(n=1):     本場指揮對比 redthread 手感；`/certsrv` 與 dev vhost 未切 UI
Reverse-test:       會害事的套用：每個 HTTP 200 都叫人開瀏覽器。閘在「互動／認證／視覺／JS 才是下一觀測」，不是凡 web 必 UI。CLI 批次枚舉、精確 header、非互動 API 仍走 ASSISTANT。
De-specified:       問題軸：這次交回是因為授權用盡，還是因為下一觀測只有人做得好？
Target-file:        references/execution-contract.md §6 應恢復接近 redthread §4 的厚度；output-contract 下一步欄要能區分兩種味道；主 SKILL 可加一句 illustration（重大若寫進 R7）
Consensus-tier:     中度（契約段加厚）；寫進 R1–R8 則重大
Status:             promoted
Subtraction:        刪掉 execution-contract 舊 §6 兩行 stub（「登入、MFA…優先考慮 UI」）。不新增 R 條、不放寬 R1。output-contract 風險卡預設 executor 從寫死 ASSISTANT 改成三選一。

四態：promoted（2026-08-14 指揮明示「這點直接改進去」；中度契約加厚，未動 R1–R8）
