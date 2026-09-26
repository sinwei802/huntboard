# HTB Preflight — 作業前檢（人機一體）

當使用者明確說 HTB／HackTheBox、提供 `*.htb`、機器名＋lab IP、或要求開機／連 VPN／交 flag 時載入本文件。  
這不是自動打穿流程，而是**開打前的可觀測檢查清單**；每一項仍遵守 STEP／HANDOFF，預設不串成同輪依賴鏈。

## 0. 原則

- 使用者是指揮；本清單產出「缺什麼／下一步建議」，不自動擴張 scope。
- 檢查本身若產生網路流量（ping、curl、nmap），標 `[ASSISTANT|USER | PRE-AUTHORIZED]` 前須已在當前授權邊界內。
- 發現 starter creds、tag、機器資訊只形成**事實**，不形成 exploit／spray 授權。
- 禁止搜尋「機器名 + writeup／walkthrough／solution」（見主 SKILL CTF 模式）。
- **開局 STOP 閘門**：preflight 檢查本身可以並行（VPN/ping/hosts 都是獨立子檢查），但 preflight 完成後**必須 STOP 並交還指揮權**。禁止 preflight 同輪自動啟動端口掃描或後續偵察。
- 指揮接著說「掃／開局／進行作戰」時，授權邊界走 `hunt-loop.md` §2.1：埠未知 → 只做傳輸面 pipeline；埠已知且觀察未完 → 具名的未認證剩餘觀察 batch。兩者都不是 exploit 授權。詳見 `hunt-loop.md`。

## 1. 連線與環境

依序用最小觀測確認（每項可獨立成 STEP）：

| 檢查 | 最小觀測 | 失敗時 |
|------|----------|--------|
| VPN | `ps`／介面／路由是否有 lab 路徑 | 回報「VPN 未就緒」；給啟動提示，**不代替使用者連 VPN** |
| L3 可達 | `ping -c 2 <IP>` 或單 port 探活 | 先分層：VPN → 路由 → 機器是否關機／換 IP |
| L7 粗探 | 對已知 web port 一次 `curl -sI --connect-timeout 5` | 空／timeout 走 `error-recovery` 網路層 |
| 本機 callback 能力 | 若鏈可能需要攻擊者聽 53/80/443 | 標註特權 port 限制（無 root／rootless）；需要時改高 port + 轉向，或標 BLOCKED 原因 |

特權 port 備註（常見於 OAuth redirect、假 DNS、bot callback）：無法 bind `<1024` 時，先改方案再深挖 payload，不要空轉。

## 2. 命名與 hosts

目標常用 `name.htb`。掃到轉址 Location、憑證 CN／SAN、或服務宣告的主機名，且本機還解析不到：這是指揮的活，不是副駕駛用協定層變通繼續打的理由。

先確認既有列；HANDOFF 用 `[USER | CONFIRM-REQUIRED]`，fence 裡放可複製的加列命令（真實 IP 與名字，禁止佔位符）：

```bash
getent hosts <IP> || true
grep -n "<IP>\|<name>" /etc/hosts || true
printf '%s %s\n' <IP> <name> | sudo tee -a /etc/hosts
```

寫入 `/etc/hosts` 預設不由 assistant 代做，除非指揮已授權代寫。剩餘 HTTP／截圖等指揮回加好了或「繼續」再打。指揮明示先不要改 hosts 時，Host 才當指紋通道。

新 hostname 先入 Asset Graph。不自動掃完全部 subdomain。Host／SNI 仍用來測**其他**尚未宣告成主名的標籤，不是用來跳過請指揮加主名。

## 3. 平台脈絡（可選、有憑證才做）

僅在使用者提供 HTB token／要求用平台功能時：

- 機器資訊、是否開機、題型 tag、官方提示級別 — 當 **metadata**，不是解法。
- Flag 提交：機器與 challenge API 欄位不同（例如 challenge 用 `challenge_id`）；不確定就查當前文件，不憑記憶。
- Container／docker 挑戰：先確認 lifecycle（start／info／expire），再對 `docker_ip:port` 做連通。

沒有平台 API 時，完全可只靠 IP＋VPN 作戰；不要阻塞。

## 4. 開局 recon 最小集（建議順序）

在「新機器、尚未建立資產圖」時，這是 **OBSERVE** 的情境層提示，不是招式表。戰役規則以 `hunt-loop.md` 為準（仍 STEP；batch 僅當使用者明確要求或開局意圖已授權一份事前列名清單）：

1. **Archetype 快掃**（heuristic，非完備 gate）：若已見目錄服務常見訊號，可優先抽樣相關 port，避免無腦先 `-p-`。  
   示例 port（illustration；未列出的 listener 不得因此降優先）：`53,88,135,139,389,445,464,593,636,3268,3269,5985,5986,9389`。  
   banner／角色不清 → `anti-blindspot.md`，不是直接 service exploit 菜單。
2. **傳輸面**：使用者說「掃」且埠未知時依 `port-scan-pipeline.md`（預設 depth=`standard`、persist=`ephemeral`，不建 `./scan`）。掃完 STOP。未解析主名見 §2；否則具名剩餘觀察 batch。
3. **剩餘觀察**（埠已知後，互不依賴）：未認證身份面、命名／vhost、取回可讀材料。HTTP 根路徑與 header、匿名／guest 檔案面只是 illustration。
4. **可讀材料優先**：本場已取回的 share／原始碼／client／binary；範圍與大檔上限見 `hunt-loop.md` §2.2。讀完不得把材料暗示的利用當寬度未完時的唯一下一刀。

觀察完成後才進 DESIGN（`tactical-search.md`）。本檔只定開局連通門檻。

## 5. 輸出

Preflight 完成後用口語 3–6 句：

- 連線是否就緒、目標怎麼稱呼、已見哪些服務 archetype  
- 缺什麼（VPN／hosts／憑證／全埠）  
- 選項欄：建議通常是傳輸面掃描；有未解析主名則 hosts 可當選項 2

不要一次丟完整 nmap 腳本牆；不要在 preflight 回合順便 exploit。
