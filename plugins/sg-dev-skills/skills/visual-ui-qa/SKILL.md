---
name: visual-ui-qa
description: Use when 已完成或可執行的 UI 需要規格比對、視覺驗收、響應式或可及性檢查，正在調查跑版、overflow、focus、互動狀態，或需要 screenshot baseline、pixel diff、CI 視覺回歸
---

# Visual UI QA

## 定位

先產生可重現、附證據的診斷，不以直覺取代觀察。預設只驗收與回報；使用者未要求修正時，不修改實作。

## 模式路由

| 使用者目的 | 模式 | 讀取／輸出 |
|---|---|---|
| 比對規格、找跑版、檢查 responsive、focus 或互動狀態 | **人工視覺 QA** | 依本檔流程，輸出 [ui-qa-report.md](templates/ui-qa-report.md) |
| 建立 screenshot baseline、pixel diff、runner 或 CI 視覺測試 | **自動視覺回歸** | 讀 [automated-visual-regression.md](references/automated-visual-regression.md)，輸出 [ui-regression-plan.md](templates/ui-regression-plan.md) |

只有使用者要求修改目標專案時，才在自動模式新增 test、config、baseline 或 CI。

## 基準確認

先確認 UI spec、驗收準則、參考圖或既有行為；記錄目標 viewport、互動路徑與可接受差異。若基準不足，列為缺少證據，不自行補成規格。

## 驗收流程

1. **啟動 gate**：確認頁面可載入，並檢查 console 沒有阻斷驗收的錯誤。無法啟動時停止，回報環境與已嘗試的步驟。
2. **證據矩陣**：以 `viewport × state × interaction` 規劃與記錄檢查。viewport 要列明尺寸與方向；state 至少涵蓋 default、loading、empty、error；interaction 要列可重現的觸發與鍵盤路徑。
3. **檢查面**：逐項觀察 layout、水平與垂直 overflow、type/color/assets、keyboard/focus（焦點順序、可見性與返回）、loading/empty/error，以及 motion 與 reduced motion。
4. **保留證據**：每個發現附截圖、錄影、console 輸出、量測或可重現觀察；不要將預期檢查寫成已觀察的證據。

## 發現分類

每個發現只能依已知基準分類為下列其中一項：

- **規格不符**：實際結果與已確認 spec 或參考基準不同。
- **實作缺陷**：可重現的功能、版面或可及性失敗。
- **參考不足**：缺少 spec、參考圖、目標狀態或可驗證環境，無法判定。
- **主觀偏好**：沒有違反基準的品味或方向建議。

## 報告

使用 [templates/ui-qa-report.md](templates/ui-qa-report.md)，依嚴重度排序。每項 finding 必須寫出 severity、分類、重現步驟、預期、實際、已捕捉或已觀察的證據，以及不擴大範圍的最小修正方向；未要求修正時只提出方向，不動程式碼。

## 停止條件與誠實邊界

環境起不來、console 有阻斷錯誤、基準不足，或尚未取得特定 viewport/state/interaction 證據時，停止對該項宣稱已完成。將它列在 `Missing Evidence` 或 `Verification Boundary`，並清楚區分已驗證、未驗證與無法判定的項目。
