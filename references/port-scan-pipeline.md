# Port Scan Pipeline — 作業契約

使用者慣用的端口掃描**邏輯**（靈感來自其 `super_rustscan.sh` 流程，已吸收為本契約）。  
**執行不依賴該 .sh**：預設直接組 `rustscan` + `nmap`。腳本若存在，僅在使用者明確要跑腳本時可選用。

**不是**「開局必跑完全埠才能往下」的宗教；是使用者說「掃／詳細度」時的**預設配方與說法**。

全埠結果 ≠ 攻擊面窮盡（仍見 `hunt-loop.md`）。掃完只形成**傳輸面**事實。開局「掃」的剩餘觀察（身份／命名／材料）走 `hunt-loop.md` §2.1，不形成 exploit 授權。

## 0. 何時載入

- 使用者要求掃描端口／rustscan／nmap 開局掃／「快掃／標準／完整／隱蔽」
- 已給明確目標（IP／hostname／CIDR／清單）且要對目標產生掃描流量
- HTB preflight 之後進入「一般主機 port 面」且使用者授權掃描

載入後遵守 SKILL 頂部 R1–R8（`execution-contract.md` 載入時機見該檔開頭）。  
**不要**為了「順便建地圖」在未授權時自動開掃。

## 1. 說法：三軸正交

口語可能只給一軸；其餘用預設補齊。

### 1.1 詳細度 `depth`

| 口語 | depth | 行為 |
|------|-------|------|
| 快掃、粗掃、peek、先看常用埠 | `quick` | 常用 TCP + 常用 UDP → 開埠 nmap `-sV -sC`（不加 `-O`） |
| 掃、標準、開局掃、全埠（未說更深） | `standard`（**預設**） | TCP **全埠** RustScan 發現 → 開埠 `-sV -sC`；UDP **常用**；可 TCP∥UDP 並行 |
| 完整、深掃、full、版本+腳本都要 | `full` | standard + `-O`；依開埠**自動**加 web／smb 類 scripts；`+vuln` 僅當口語要求 |
| 隱蔽、stealth、小聲 | `stealth` | 覆蓋同 standard，rate=`low`；傾向串行、較慢 batch |
| 中掃、top、top1k（可選） | `top` | TCP `--top-ports 1000`（nmap 發現或等價）+ 常用 UDP |

### 1.2 落盤 `persist`（與 depth 無關）

| 口語 | persist | 行為 |
|------|---------|------|
| 沒說、看一下、別建目錄、只掃、不要 ./scan | `ephemeral`（**預設**） | 輸出進 **mktemp 目錄** 或 stdout 解析；摘要進對話；未要求保留則刪 tmp |
| 存檔、留 nmap、寫到 scan、落到 ./scan | `workspace` | 預設 `./scan`（或使用者給的路徑） |
| 進 engagement／pentest-state／留證據 | `engagement` | 寫入已約定之 `./pentest-state/loot/`（或指定子路徑）；**不**自動 checkpoint 五核心檔 |

硬規則：未說存檔 → **禁止** `mkdir scan`／污染 cwd。

### 1.3 範圍修飾（可疊加）

- `tcp-only`／`udp-only`／`udp-full`／自訂 UDP 埠表
- `rate low|normal|high`（未說：standard→normal，stealth→low，quick→normal）
- scripts：`+vuln` `+web` `+smb`（顯式優於 full 自動選擇）
- 目標：單 IP、多 IP、CIDR、檔案列表

### 1.4 口語 → 參數速查

```text
掃 10.10.11.23
  → depth=standard persist=ephemeral rate=normal

快掃 10.10.11.23，只要 TCP
  → depth=quick persist=ephemeral tcp-only

完整掃 10.10.11.23，結果放到 ./scan
  → depth=full persist=workspace dir=./scan

隱蔽掃 10.10.11.0/24，存檔
  → depth=stealth persist=workspace rate=low
```

## 2. 執行原則（不綁 .sh）

| 優先 | 方式 | 何時 |
|------|------|------|
| **1（預設）** | 直接 `rustscan` + `nmap`（本檔 §3） | 一律 |
| 2 | 使用者指定「用 super_rustscan／跑那支 sh」 | 僅明示 |
| 3 | 僅 `nmap` | `rustscan` 缺失時降級並口語說明 |

- **邏輯真相在本 reference**，不在 filesystem 上某支腳本是否存在、是否改版。
- 缺 `rustscan`：TCP 發現改 `nmap -Pn -p- --min-rate …` 或 top-ports（依 depth），不中止整輪裝死。
- 缺 `nmap`：回報依賴缺失；不用無關工具假裝同深度服務識別。
- `sudo`：需要 raw/SYN 且無權時再提升；已有 capability／root 則不必硬塞 sudo。失敗則診斷權限，不改 scope。

### 2.1 persist 目錄

```bash
# ephemeral（預設）— 用 engagement workspace 下的隱藏目錄，不用 /tmp（避免被其他程式污染）
outdir="./.scan-tmp"
mkdir -p "$outdir"
# 掃描 -oN/-oA 指到 $outdir；解析後摘要進對話
# 使用者未要求保留 → rm -rf "$outdir"

# workspace
outdir="${SCAN_DIR:-scan}"; mkdir -p "$outdir"

# engagement（須已有 engagement 語境或使用者指定路徑）
outdir="./pentest-state/loot/scan"; mkdir -p "$outdir"
```

engagement 勿擅自建五核心狀態檔。所有掃描與工具輸出一律放在 engagement workspace 下（ephemeral 用 `./.scan-tmp/`，workspace 用 `./scan/`，engagement 用 `./pentest-state/loot/`），**禁止使用 `/tmp`**（避免被其他程式污染或互相干擾）。短命 staging 用完可刪。

### 2.2 授權與 STEP

- 同一則訊息已寫明目標 + 掃／詳細度 → 該次掃描 `[ASSISTANT | PRE-AUTHORIZED]`（只要命令則 `USER`）。
- 一次 Target STEP = 對已列名目標的一輪 port pipeline（TCP 發現→深掃與 UDP 可同輪並行）。
- 掃完 **HANDOFF**：解析 → 作業脈絡 Asset Graph → 相位保持 OBSERVE。若本則出現未解析的已宣告名字，下一步是 `[USER]` 加 hosts（`htb-preflight.md` §2），剩餘觀察寫在加完之後。否則具名剩餘觀察 batch（identity_unauth／naming／materials，參數用本則已見的 listener），或指揮已另具名的單一步。禁止同輪自動把掃到的 port 拿去 exploit。gobuster／nxc 等未認證取樣只有寫進該具名 batch 才算授權。
- 大 CIDR：先確認範圍與 rate；必要時先 host-discovery（另 STEP）。

## 3. Pipeline（直接工具）

### 3.1 常數

```text
COMMON_TCP=21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5432,5900,8080,8443

COMMON_UDP=7,19,37,53,67,68,69,88,111,123,135,137,138,139,161,162,177,389,427,443,445,464,500,514,520,623,631,636,749,750,993,995,1194,1434,1701,1723,1812,1813,1900,2049,2302,3478,3544,4000,4500,5060,5353,5632,6000,51820

# RustScan -b / -t
rate low    → -b 1500 -t 3000
rate normal → -b 4500 -t 1500
rate high   → -b 8000 -t 800
```

### 3.2 TCP 發現（RustScan）

```bash
# quick
rustscan -a "$target" -p "$COMMON_TCP" -b "$batch" -t "$timeout" -g

# standard | full | stealth（全埠發現）
rustscan -a "$target" -b "$batch" -t "$timeout" -g

# top：無 rustscan top 時
nmap -Pn --top-ports 1000 -oG - "$target"   # 再抽 open
```

解析 greppable：目標列上 `[port,port,…]` → 開埠 CSV。無開埠 = `NO_PORTS`（成功無面），不是工具崩潰。

### 3.3 TCP 深掃（有開埠才跑）

```bash
# standard / quick / stealth / top
nmap -Pn -sV -sC -p "$tcp_ports" -oN "$outdir/${id}_tcp.nmap" "$target"

# full：加 -O；scripts 見下
nmap -Pn -sV -O -sC [script args] -p "$tcp_ports" -oN "$outdir/${id}_tcp.nmap" "$target"
```

Scripts：

- 顯式 `+web` 或 full 且開埠含 80/443/8080/8443 等 → `--script=http-enum,http-headers,http-methods`（可與 `-sC` 並用，注意重複無害）
- 顯式 `+smb` 或 full 且 139/445 → `--script=smb-enum-shares,smb-enum-users,smb-os-discovery`
- 顯式 `+vuln` 才加 `--script=vuln`（不因 full 自動全開）

可把開埠列表另存 `$outdir/${id}_tcp.ports`。

### 3.4 UDP

```bash
# 預設常用；udp-full → 1-65535（須使用者知情，極慢）
nmap -Pn -sU -sV -sC --version-intensity 0 --host-timeout 15m --max-retries 2 \
  -p "$udp_set" -oN "$outdir/${id}_udp.nmap" "$target"
```

從 nmap 抽 `open` 與 `open|filtered` 寫入 `${id}_udp.ports`（若有）。

### 3.5 並行與 stealth

- 預設：同目標 TCP pipeline 與 UDP 可背景並行（兩條命令）。
- stealth 或使用者要穩：串行；rate=low。
- tcp-only / udp-only：跳過另一側。

### 3.6 無 RustScan 降級

| depth | 降級 TCP 發現 |
|-------|----------------|
| quick | `nmap -Pn -sS -p "$COMMON_TCP"`（或 `-sT`） |
| top | `nmap -Pn --top-ports 1000` |
| standard/full/stealth | `nmap -Pn -p-` 加合理 `--min-rate`（stealth 降低 rate） |

再對開埠做與 §3.3 相同深掃。

## 4. 解析與回報

優先讀：`*.ports` → `*.nmap` 服務／script 行 → 自行彙總。

掃完 **先區塊、後選項欄**（`output-contract.md` §1.2）。區塊用 `markdown` code fence，裡面是可貼進 Obsidian 的原文。指揮從區塊複製；禁止只渲染表，也禁止叫人去開 md 檔。不要一次貼完整 nmap 腳本牆。僅 banner 未證實的欄位在備註標 `[?]`。

區塊內標題與欄位（照抄這個形狀）：

~~~markdown
### 傳輸面

#### TCP
| 埠 | 協議 | 狀態 | 服務 | 產品／版本 | 備註 |
|----|------|------|------|------------|------|

#### UDP
| 埠 | 狀態 | 服務 | 備註 |
|----|------|------|------|

### 主機身份（<來源，未登入>）
| 欄位 | 值 |
|------|----|
~~~

無 TCP 開埠：仍出表，一列寫 `NO_PORTS`（成功無面，不是工具崩潰）。  
UDP 只列 `open` 與 `open|filtered`；後者備註必須寫「未確認開啟」。常用埠全無回應時可收成一列摘要，不要假裝掃過全 UDP。  
主機身份只放已看到的電腦名／網域／OS 版本／憑證 CN。沒有就不建這張表。

然後才是選項欄：

```text
新事實：<開埠與服務／版本的一句摘要；無埠也說清>
判斷：<角色假設；僅 banner 標 [?]>
態勢：Goal=辨識傳輸面暴露 · 下一探=<具名剩餘觀察 batch>

選項：
1. [建議] [EXECUTOR | APPROVAL]：<具名剩餘觀察 batch：身份面／命名／可讀材料>
   預期：<匿名／guest 能列到什麼／讀到什麼>
   風險／停：取樣完即停；不用掃到的 listener 去 exploit／登入
   為什麼現在：傳輸面已見，下一刀補未認證寬度
2. [USER | CONFIRM-REQUIRED]：<若已宣告名字本機還解析不到：加 hosts>
   預期：本機可解析後剩餘觀察才打到對的名字
   風險／停：只改本機 vantage
   為什麼現在：憑證／NTLM 已宣告主名時，這條排前面
```

Asset Graph（作業脈絡）：`host → ports/proto → service/product/version → evidence`。  
ephemeral 已刪檔：evidence 標 `ephemeral-session`，關鍵列已在對話即可。

## 5. 來源與獨立性

本契約的掃描邏輯自足，直接組 `rustscan` + `nmap` 執行，不依賴任何外部腳本。

## 6. Guardrails

- 無明確目標／scope → 只問目標，不掃。
- 「掃」≠ 授權 spray、exploit、寫 `/etc/hosts`、建 pentest-state 核心檔。
- 同一 depth 無新軸重跑 → 計態勢列 attempts，避免空轉。
- `NO_PORTS` ≠ 主機必死者：vantage／filter／UDP／時機可能未測。
- CTF：不搜機器名+writeup。
- 本檔 = **傳輸面取樣工具契約**；命名／內容／身份軸與開局 batch 見 `hunt-loop.md`。戰術展開見 `tactical-search.md`。

## 7. 使用者只要命令時

`executor=USER`：依三軸印出**直接** rustscan/nmap 可複製命令（可含 outdir=mktemp 兩行），不代跑。Block 內純命令、無佔位符（缺目標先問）。不要預設貼 `.sh` 包裝除非使用者要。
