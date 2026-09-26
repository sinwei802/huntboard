# doctrine-compatible-privesc

> **繁中**：提權分流：在禁 PoC／禁菜譜下判斷下一刀是否相容（證據門）。


## 何時用

- 提權相位枚舉後，要決定「下一刀能不能在禁 PoC／禁菜譜編制下打」。
- 三分流：相容 misconfig 成功形 vs 無面需 PoC 不相容 vs 有面但程序／平台拒批。

## 要驗證什麼

1. 本場 finding 是否屬**設定／授權錯誤類**（例：sudoers 具名 NOPASSWD 二進位、可驗證的錯誤委派）——可走「列舉 → 指揮批單段驗證 → 記 uid／flag」，戰情**不需**逐步 exploit 菜譜。
2. 若唯一續打路徑＝公開 CVE 堆／需撰寫或投送 PoC／binary exploit → 標 **`DEAD:doctrine-incompatible`**（或 `GAP:needs-retarget`），立刻 HANDOFF：停火／請靶場主改 misconfig 類靶——**不是**偷懶，也不是叫副駕駛寫 PoC。
3. 不得把「版本號吻合某 CVE」單獨當 owner 達標；達標仍只認 root flag 證據（見 `owner-root-flag-bar`）。

## 證據長什麼樣

| 相容（可續） | 不相容（停＋交班） |
|---|---|
| `sudo -n -l` 具名允許＋授權內驗證出 uid=0 | 僅舊套件版本＋需堆利用才能升權 |
| 異常 SUID／capability **本場可驗證行為**且不需 PoC 正文 | 必須貼 exploit／編譯 PoC 才有下一刀 |
| docker.sock 等面：只記有無；利用級另批且仍禁菜譜進 vault | 無 misconfig 面卻逼 exploit |

## HANDOFF 句式（不相容時）

「枚舉完成；經典 misconfig 無面；續打需 PoC → `DEAD:doctrine-incompatible`。請指揮停火或請靶場主改設定錯誤類靶。owner 未達（無 root flag）。零 PASS。」

## 第三態：面相容但程序／平台拒批

枚舉已見設定錯誤類面（例：高權排程呼叫低權可寫腳本），但指揮 DENY 或執行席安全閘拒「改寫腳本／誘發高權」：

- 標 **`DEAD:platform-deny`**（或 `HOLD:await-owner-policy`）——**不是** `doctrine-incompatible`（那是「無 misconfig 面」）。
- HANDOFF：停火；請靶場主／主人裁「本場是否允許授權內改寫已枚舉可寫腳本」或誠實結案未達標。
- 戰情只記路徑／權限／拒批理由；**不**寫改檔內容／排程誘發步驟。

HANDOFF 句式：「枚舉完成；相容 misconfig 面已記；續打需改寫可寫腳本＝利用類 → 指揮／閘 DENY → `DEAD:platform-deny`。owner 未達。零 PASS。」

## 禁

- payload／PoC／CVE 逐步利用進本卡或戰情。
