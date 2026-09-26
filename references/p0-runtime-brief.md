# P0 Runtime Brief — 給 Hermes 維護者的需求（含新增 P0-RT-5）

> 對象：Hermes / gateway / harness 層維護者。不是 skill 文字；是 runtime 級硬停的提議與 API 形狀。
> 對應問題：弱模型即使在頂部紅線 R1–R7 載入下，仍會被 `finish the job` / `tool_persistence` / 「作完再停」壓過，繼續同輪發射碰目標呼叫。
> 純文字 patch 對此上限約 6–7/10；本 brief 提議 runtime 機制把上限推到 9/10。
> 共識來源：2026-08-11 Hunter × Claude（弱模型 HITL）。

## 1. 為什麼純文字擋不住

- 系統 prompt 在多數 harness 中**優先級高於 skill**。
- 弱模型對判斷題永遠選對自己寬鬆那邊；即便規則可數，生成階段仍可能把兩個獨立偵察合進一回合。
- Skill 是**宣告性**；runtime 是**強制性**。兩者需分工。

## 2. P0-RT-1..4（移植自 redthread，格式微調）

### P0-RT-1　回合 Target 硬停（最高槓桿）
同一 assistant turn 內，第一個「碰目標」工具結果返回後，harness 拒絕再調度更多碰目標工具（純 Research 可繼續）。判定靠 tool registry 的 `touches_target: bool`（terminal/web 預設 true，read/search 預設 false，skill 可覆寫）。實作於 tool 調度層（per-turn 計數器 + 拒絕佇列）。擋下約 80% 同輪連鎖。

### P0-RT-2　系統 prompt 優先級宣告
huntspear 啟用 profile 時調整注入層順序（skill_frontmatter > skill_body > profile > finish_the_job），或對 finish-the-job 段 `when_skill_active: suppress|defer_to_skill`。解 R6 誠實邊界核心；改動大。

### P0-RT-3　輸出 lint
回應含 tool call 但缺 `下一步 [EXECUTOR | APPROVAL]` 標籤，或標籤後仍有碰目標 tool call → 拒送重問。與 P0-RT-1 互補（一個卡 tool 發射、一個卡輸出形狀）。

### P0-RT-4　寫入類 tool 旗標
對會改目標狀態的命令模式（certipy req/shadow、UPN/ACL、impacket secretsdump/wmiexec/psexec、pywhisker、持久化）要求使用者 inline 確認，正面攔截而非事後。pattern 由各 skill 自帶宣告（去中心化）。

**期望**：文字到位 runtime 不到位 → 6–7/10；runtime 到位文字不到位 → 5/10；兩者到位 → 9/10。

### Hunter 落地現況（2026-08-14，指揮授權）

| 項 | 狀態 | 位置 |
|---|---|---|
| P0-RT-1 第二次碰目標拒絕 | **Hermes Hunter 選配已落地** | 選配 runtime plugin（套件 id `huntspear-runtime`，本 skill 的選配 runtime plugin id；在 Hermes profile 的 `plugins/` 下）。`./pentest-state`、`htb/` cwd、或本場已載入 huntspear 時武裝。不是 skill 套件的一部分；Claude 預設沒有 |
| P0-RT-2 系統提示優先級 | **未完成** | plugin 只在 system 區塊**末尾**追加延期宣告，不能刪掉 Finishing the job |
| P0-RT-3 輸出 lint | **未做** | `llm_execution` 形狀未證實；先靠 R7 契約 + P0-RT-1 |
| P0-RT-4 寫入類命令確認 | **未做** | 仍靠 R4 契約 |
| P0-RT-5a canonical 寫入閘 | **已落地** | 同 plugin；env `HUNTSPEAR_WRITE_OK=1` 才放行 SKILL／契約層 |
| P0-RT-5b promote lint | **未做** | auto-promote 維持關 |
| 內建 loop hard_stop | **已開** | Hunter `tool_loop_guardrails.hard_stop_enabled=true`，`exact_failure=2` |

現況期望值約 **7–8/10**。到 9/10 仍缺真正的 P0-RT-2。

## 3. 【新增】P0-RT-5　skill 檔寫入閘 + 學習回路升級 lint

對應 huntspear 的學習回路（§10 / `learning-loop.md`）。**這兩者現在都不存在 → 所以 auto-promote 維持關**（Q7）。

### (a) skill 檔寫入閘
沒有 approval token 就擋掉對 huntspear **canonical 檔**（SKILL.md、契約層 ref、紅線）的編輯。類 P0-RT-4，但針對 skill 檔本身。目的：弱模型可能把 target-specific 噪音自我升級進 canonical——正是要防的污染。

```yaml
skill_write_gate:
  protected_paths:
    - "SKILL.md"
    - "references/execution-contract.md"
    - "references/output-contract.md"
    - "references/state-schemas.md"
    - "references/learning-loop.md"
  candidate_area: "references/candidate-patches/**"   # 免閘，可自由寫
  on_write_without_token: refuse
  approval_token: dual_consensus_signature            # named-peer（Claude）簽核
```

### (b) 學習回路升級 lint
auto-promote 落 canonical 前，驗證候選卡的泛化測試欄位齊備：`Sightings(n)` ≥ 門檻（心法/route ≥2、gate ≥3）、`Reverse-test`、`De-specified`、`Consensus-tier`、`Subtraction` 皆已填。任一缺 → 拒絕升級、退回隔離區。

```yaml
promote_lint:
  require_fields: [sightings_n, reverse_test, de_specified, consensus_tier, subtraction]
  min_sightings: { mindset: 2, route: 2, gate: 3 }
  on_missing: reject_promote_keep_quarantined
```

**含意**：P0-RT-5 到位前，auto-detect + auto-draft（進隔離區）可開；auto-promote（落 canonical）維持人閘。**auto-promote = 紙上設計（等 P0-RT-5）；人閘進化 + auto-detect/draft = 今天能跑。**

## 4. 誠實邊界

R6 橫幅已在 SKILL.md 頂部，不另立檔。另一條：雙強共識依賴 named-peer（Claude）auth 可用；auth 失敗時「重大」級無法落地 → 必須 STOP + HANDOFF，不得 silent 換 CLI。共識閘可用性 = Claude auth 可用性。

## 5. 交付順序（給維護者排程）

1. **P0-RT-1**（最高槓桿、改動小）→ 立刻擋 80% 同輪違規。
2. **P0-RT-3**（改動小、互補）。
3. **P0-RT-5**（skill 寫入閘 + 升級 lint）→ 讓 auto-promote 可安全開啟。
4. **P0-RT-2**（注入層，大改動）。
5. **P0-RT-4**（各 skill 自帶 pattern）。

## 6. 引用

- SKILL.md 頂部紅線 R1–R8 + 思維卡 T1–T3
- `references/execution-contract.md` §11（同方向／同面／授權時效／失敗兩次停）。P0-RT-1 仍是「第一個碰目標就硬停」；與現行 R1（方向內可覆核）不一致，runtime 尚未跟著放寬。
- `references/learning-loop.md`（§10 詳解）
- DanglingTree 會話違規樣本（2026-08-11）
