# priv-esc-evidence-gate

> **繁中**：提權證據門：升級前要驗證什麼、死路與交叉禁 PoC 分流。



## 何時用

- post-foothold 地圖已有至少一個 **verified** finding class，要決定「權限擴張相位」是否開門。
- 從 privesc-evidence 邁向 root／DA **確認準則**之前（只談門檻與枚舉順序，不談怎麼打）。

## 要驗證什麼

1. 每個候選門是否綁定本場事實（ACE 類別、群組成員、capability／SUID **標籤**、可寫設定類）而非訓練記憶中的「經典路徑」。
2. 門的狀態是否為：`open-for-observe`｜`open-for-enum`｜`closed`｜`unknown`——`unknown`／`closed` 不得當達標依據。
3. 升級提案是否仍是方法論動作（observe／enum／dead-path／查公開文件）；利用級 `action_class` 在無完整 sense 時必須被拒。

## 證據長什麼樣

建議閘門表（寫進戰情即可）：

| 欄 | 含義 |
|---|---|
| Gate ID | 本場短碼（G1…） |
| Finding class | 抽象類別名（例：`acl-object-write`、`interesting-capability-or-suid`） |
| Observed fact | 一句可複核觀測 |
| Gate open when | 具體條件；未滿足＝關 |
| Blocks | 明確禁止的下一步類型（payload／poc／exploit-recipe） |

合格達標前（root／DA）另需：身份證明觀測（例：uid=0 或 Domain Admins 成員）＋全鏈 stage 完整——本卡只開「准否繼續蒐證／確認」，不開「怎麼利用」。

## 死路怎麼標

- 無本場 finding 却用題名／記憶補鏈 → `DEAD:hypothesis-mismatch` 並 REJECT。
- 有 finding 但只能靠利用菜譜前進 → `GAP:no-local-playbook`，只准補卡／查公開概念，不准 exploit。
- 偽造成功（準則未 verified）→ `DEAD:hypothesis-mismatch`；回上一 stage。
- 方法論破口（payload／PoC／writeup）→ `DEAD:methodology-breach`。

## 去哪查

- 本庫：`post-foothold-map`、`evidence-gate`、`dead-path-mark`、`public-doc-cve-lookup`。
- 公開：權限模型／sudoers 語意／AD 委派**概念**——非利用庫。
- **紅線**：無 exploit 指令、無 PoC、無 reverse shell、無 flag 路徑、無 writeup URL。

## 與禁 PoC 編制（2026-09-26）

- 續打前對 `doctrine-compatible-privesc`：無 misconfig 可驗證面、只剩需 PoC 的路徑 → 標不相容並 HANDOFF，禁止硬寫 exploit。
- owner 達標對 `owner-root-flag-bar`：中間旗≠過關。
