# Sense-cards ↔ Vault 薄 playbook 對照

防雙源漂移。**Runtime 真源＝本 skill 樹**；vault 供人讀／週一雙軌改善後再回寫 skill。

| sense-cards（skill） | Vault PB 卡 | 職責（方法層） |
|---|---|---|
| `http-observe-only.md` | `PB-HTTP 只觀察.md` | HTTP 面只觀察／往返指紋 |
| `evidence-gate.md` | `PB-證據門.md` | 升級前證據門 |
| `dead-path-mark.md` | `PB-死路標記.md` | 死路／重開條件 |
| `public-doc-cve-lookup.md` | `PB-公開文件與 CVE 查法.md` | 公開文件／CVE 查法（非利用） |
| `local-sense-memory.md` | `PB-本地 sense 要記什麼.md` | 戰情該記什麼 |
| `post-foothold-map.md` | `PB-站穩後地圖.md` | foothold 後列舉／地圖（非利用） |
| `priv-esc-evidence-gate.md` | `PB-提權證據門.md` | 提權相位證據門／枚舉順序（非利用） |
| `web-app-evidence-ladder.md` | `PB-Web 達標證據階梯.md` | Web／訓練應用達標階梯 |
| `challenge-board-handoff.md` | `PB-挑戰盤交班.md` | 挑戰盤→可稽核下一階句式 |
| `session-break-rebuild.md` | `PB-工作階段斷裂重建.md` | infra 斷裂後重建 checklist |
| `owner-root-flag-bar.md` | `PB-主人尺 root flag.md` | 只認 root flag |
| `doctrine-compatible-privesc.md` | `PB-提權與禁 PoC 相容.md` | misconfig vs 需 PoC 分流 |
| `post-engagement-retro.md` | `PB-結案复盤.md` | 成敗都迭代 |
| （總則）`local-sense.md` | `HuntSpear 薄 playbook.md` | 強制程序／與手法 playbook 切開 |
| （總則）`cloud-sources.md` | `雲端資料來源登錄.md` | 多源登錄與增刪 |

## 回寫規則

1. 改 vault 卡 → 同週把同等方法句同步進對應 sense-card（禁止只改一邊）。
2. 改 sense-card → vault 鏡像更新；CHANGELOG 記一筆。
3. **禁止**把 payload／PoC／逐步利用寫進任一側。
4. 衝突：以 skill 樹 + 較新 CHANGELOG 為戰鬥準；vault 註「待同步」。
