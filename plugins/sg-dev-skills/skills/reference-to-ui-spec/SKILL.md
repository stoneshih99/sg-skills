---
name: reference-to-ui-spec
description: Use when 使用者提供截圖、影片、網站、HTML、wireframe 或模糊視覺方向，希望分析、重製、借用視覺語法，或先整理成可交付工程實作的 UI 規格
---

# Reference to UI Spec

## 定位

只把 reference 編譯成可驗收的 UI spec，不實作 UI。

## 輸入確認

確認可存取的參考、目標使用者與平台，以及原創邊界與權利狀態。未確認所有權或授權時，只能借用結構、互動語法或高階視覺方向，不得複製品牌內容或受限素材；使用者確認自有或已授權的資產與內容，則可在 `Reference Boundary` 記錄重製範圍後使用。

## 證據優先規則

- 有原始 HTML 時，以可觀察到的結構、內容與行為為準。
- 有影片時，擷取各狀態的關鍵畫面後再描述轉換。
- 靜態圖只能描述可見結果；不可推斷精確動畫技術、時序或實作方式。

## 分析層

在 `Evidence` 中將可由參考直接證實的 **Observations** 與為補足規格而提出的 **Assumptions** 分開。沒有手機參考時，手機的布局、優先順序與斷點一律標示為假設。

## UI Spec Workflow

依序完成：goal → layout → type/color → assets/content → states → motion → responsive → accessibility/performance → acceptance。每一步只寫可驗收的視覺、內容、互動或限制，不寫元件程式、框架選擇或部署步驟。

## 停止條件

若參考不可存取，或存在會改變整體方向的矛盾，提出一個阻斷問題後停止；不要以猜測補齊。

## 輸出

複製 [templates/ui-spec.md](templates/ui-spec.md) 的所有欄位並填寫；輸出不得夾帶實作或部署內容。

## 常見錯誤

- 只描述風格，沒有資訊層級、內容與互動狀態。
- 把猜測寫成來源事實。
- 漏掉手機行為或元件狀態。
- 未確認權利便直接抄錄品牌名稱、文案、圖像或其他受限內容。
