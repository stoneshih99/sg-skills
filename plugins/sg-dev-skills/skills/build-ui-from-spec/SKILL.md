---
name: build-ui-from-spec
description: Use when 使用者已有 UI spec、wireframe、設計 brief 或明確頁面需求，要求在 HTML、React、其他前端技術棧或 Unity UI 建立、修改或完成可執行介面
---

# Build UI from Spec

## 定位

只負責實作已確認的 UI spec，不重新發明設計方向。缺少可執行規格時，先建立最小 build brief；若連視覺與互動規格也缺，先使用 `reference-to-ui-spec` 整理。

## 專案先行

在新增元件前，先讀取專案 instructions、UI design system、design tokens、既有 components、scripts 與 tests。建立需求到現有 token／component 的 reuse map；現有系統能滿足需求時，先重用而非另建。

## Build Brief

先依 [templates/ui-build-brief.md](templates/ui-build-brief.md) 建立 brief，鎖定 route 或 screen、stack、reuse inventory、內容與資料、元件與 states、交付形式和 non-goals。任何超出這些邊界的設計或架構決策，先向使用者確認。

## 工具選擇

依目前 runtime 與專案已安裝的工具選擇執行方式，先確認能力可用再開始：網站可使用 Sites、既有前端 stack 或瀏覽器；既有專案優先沿用其 scripts；Unity UI 交由 Unity 專屬知識處理。不可假設部署能力或新增未確認的工具。

## 實作順序

依序完成：

1. 結構與資料：先讓 route 或 screen 使用既有 tokens、元件與真實或明確的 mock 資料。
2. Responsive：再完成各 viewport 的重排、溢位與內容優先順序。
3. States 與 interactions：逐一實作 spec 所需的 default、loading、empty、error、success、hover 與 focus 狀態。
4. Motion：只加入 spec 要求的動態效果，並提供 reduced-motion 行為。
5. Polish：最後調整視覺細節，不改變已鎖定的結構、stack 或交付範圍。

## 驗證

依 build brief 的實際 commands 啟動並檢查 console。驗證目標 viewport、鍵盤操作與焦點可見性，以及 loading、empty、error 和 success 狀態；同時確認 reduced motion 生效。

需要 visual regression 時，優先沿用 fixture、Storybook、test route 或 mock，讓資料、時間、locale、timezone、theme、animation 與 network outcome 中必要的項目 deterministic。記錄每個 viewport／state／theme 的可重現觸發方式；不要為單次畫面另建抽象框架。

將實際跑過的 commands、檢查過的畫面或截圖與尚未驗證項目分開記錄。

## 交付

交付時列出改動、可重現的驗證證據、各狀態的觸發方式與未穩定項目。只有使用者明確要求時才部署；未部署不得暗示已可發佈。

## 常見錯誤

- 忽略既有 design system 與 components，先造新元件。
- 只完成 happy path，漏掉 loading、empty、error 或 focus 狀態。
- 畫面可手動操作，但沒有可重現觸發方式，導致回歸測試不穩定。
- 用靜態截圖冒充可執行且已驗證的介面。
- 未確認 runtime 或工具能力就擅自換 stack 或部署。
