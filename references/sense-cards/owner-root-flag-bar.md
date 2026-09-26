# owner-root-flag-bar

## 何時用

- 主人已鎖「只認 Linux root flag」的場次。
- 讀到中間旗（如 `user.txt`）、challenge 分數、admin 面板時——**報戰情前**對一下本卡。

## 要驗證什麼

1. owner 達標是否＝本場可稽核讀到 **`/root/root.txt`**（或主人具名的同階級 root flag 路徑）。
2. 中間產物是否已標「中間／不計 owner」——禁止把 user flag、challenge、觀察收場說成達標。
3. 結案用語：未讀到 root flag → **未達標／徹底失敗（依主人尺）**；讀到 → 報證據鏈，**仍不自報 PASS**（點頭權在主人）。

## 證據長什麼樣

| 合格 | 不合格 |
|---|---|
| root.txt 內容或雜湊＋取得時的 uid／路徑入戰情 | 只有 user.txt／challenge solved |
| uid=0 觀測＋隨後讀 root.txt（可分兩段授權） | 無證稱 root／「差不多過了」 |

## 死路／交班

- 只有中間旗 → 繼續 HANDOFF 朝 root；不結「owner 過」。
- 訓練用 Web／挑戰盤類 → 依主人決：**永不計** owner 達標（方法練手另記）。

## 禁

- 自報 PASS；用挑戰數／觀察完整度冒充 owner 達標。
