# 自動視覺回歸

## 建立前提

先確認：

- 可執行且狀態可重現的 UI。
- 經產品或設計確認的正確 baseline authority。
- 專案現有 test runner、啟動命令、snapshot 慣例與 CI artifact 能力。
- 需要覆蓋的 viewport、theme、state 與 interaction。

沒有正確性依據時只能建立 regression plan，不能把首次截圖自動核准為 baseline。

## Coverage Matrix

使用最小風險矩陣，不預設所有維度都做完整笛卡兒積：

| 維度 | 常見選項 | 選取原則 |
|---|---|---|
| Viewport | wide、narrow、orientation | 版面或內容優先序會改變 |
| Theme | light、dark、brand theme | token 或 asset 會改變 |
| State | default、loading、empty、error、success | 結構或訊息會改變 |
| Interaction | focus、expanded、selected、modal | 截圖能穩定停留且有風險 |

完整組合成本過高時，記錄代表性矩陣的選取理由與未覆蓋風險，不默默刪除案例。

## Deterministic Environment

依案例固定實際會影響渲染的項目：

- Data fixture、排序、亂數與 network outcome。
- Date、time、timezone、locale 與格式化結果。
- Theme、viewport、device scale 與 browser/version。
- Font readiness、image readiness 與 lazy-loaded media。
- Animation、transition、caret、cursor 與 reduced motion。
- Browser storage、feature flags、A/B variant 與 permission state。

優先使用既有 fixture、Storybook、test route、mock 或 runner capability。不要只靠任意 sleep 等待不確定狀態。

## Baseline 規則

1. 先以 spec、已核准 reference 或人工 review 確認畫面正確。
2. 記錄 baseline owner、產生環境、case ID 與核准理由。
3. Baseline 更新必須是顯式 reviewed action；更新前先讀 expected、actual 與 diff。
4. 不用 update snapshot 掩蓋未知 regression。

## Threshold 與 Mask

- 預設追求穩定輸入，不先放寬 threshold。
- Threshold 只吸收已證實的 renderer 或 anti-aliasing noise，不吸收 layout、color、content 或 asset drift。
- Mask 只遮真正不可固定且不屬於驗收範圍的窄區域；記錄 selector、原因與風險。
- 不遮整個 component、主要內容或正在驗證的互動結果。

## 失敗診斷

每個失敗保留：

- Case ID 與重現 command。
- Expected、actual、diff artifacts。
- Runtime、viewport、theme、locale、state 與 fixture。
- 分類：layout regression、content drift、asset/font readiness、rendering noise、environment mismatch 或 intentional change。

先修正輸入不穩定或實作缺陷，再決定是否更新 baseline。

## CI 契約

- 使用與本機一致的 browser/runtime 版本與字型資產。
- 失敗時上傳 expected、actual、diff 與 runner log。
- Case 可以依同一份 plan 在本機重現。
- Baseline update 不由一般 CI failure 自動觸發。
- 新增或修改 baseline 時，reviewer 能看出視覺變化與原因。

## 交付

先依 [UI regression plan](../templates/ui-regression-plan.md) 鎖定契約。只有使用者要求修改目標專案時，才新增 test、config、baseline 或 CI；預設 QA 模式只回報計畫、證據與缺口。

## 常見錯誤

- 把第一次跑出的畫面直接視為正確 baseline。
- 用寬 threshold 或大範圍 mask 讓測試「穩定」。
- 依賴 live API、當前時間、未固定 locale 或未載入完成的字型。
- 只保存 diff，不保存 expected、actual 與重現 command。
- 視覺變更未 review 就批次更新 snapshots。
