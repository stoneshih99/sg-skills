# 抽取 UI Design System

## 證據優先順序

依可信度使用來源：

1. 既有 design tokens、theme、元件 API 與程式碼。
2. 可檢查的 HTML/CSS 與多頁實際畫面。
3. 附環境資訊的截圖或 evidence manifest。
4. 單張視覺參考。

程式碼中的精確值可記為 observed；由截圖量測或歸納的值標示 inferred；為填補系統缺口而新增的決策標示 proposed。

## 抽取流程

1. 界定來源頁面、元件、theme、viewport 與權利範圍。
2. 先找重複的視覺和互動角色，再建立 token；不要把每個原始值都命名。
3. 將 tokens 分層：
   - Primitive：原始 color、size、font、duration 或 easing。
   - Semantic：surface、text、border、accent、spacing role 或 motion role。
   - Component：只在元件 contract 需要時引用 semantic tokens。
4. 盤點 typography、spacing、radius、elevation、motion、breakpoint、icon 與 asset 規則。
5. 列出 component、variant、size、state、responsive behavior 與 content constraint。
6. 分開 reusable pattern 與 one-off composition。一次性 hero 或 campaign layout 不要偽裝成通用 component。
7. 建立 reuse map：現有元件／token、可直接重用範圍、缺口與建議新增項目。
8. 列出同義 token、近似值、命名衝突、缺少 state 與仍需產品裁決的問題。

## Token 判準

| 情境 | 處理 |
|---|---|
| 多處共享同一語意角色 | 建立 semantic token |
| 只有數值相同但角色不同 | 分開命名，不因巧合合併 |
| 同一角色有多個近似值 | 記錄 drift，提出收斂候選 |
| 截圖只能估算數值 | 標示 inferred 與容許誤差 |
| 目標專案已有 schema | 映射到既有格式 |
| 沒有 machine-readable schema | 只輸出語意規格，不擅自發明 `tokens.json` schema |

## Component Contract

每個 component 至少記錄：

- Purpose 與 content role。
- Existing implementation 或 planned owner。
- Variants、sizes 與 states。
- Keyboard、focus、touch 與 disabled behavior。
- Responsive collapse、wrap、overflow 或 density rule。
- 使用的 semantic tokens。
- 可組合邊界與 one-off exceptions。

## 輸出

使用 [UI design system template](../templates/ui-design-system.md)。只有使用者要求修改目標專案，且專案已有明確 token／component schema 時，才另外建立機器可讀檔案或修改實作。

## 常見錯誤

- 從一張截圖宣稱得到精確 token。
- 以原始 hex 或 pixel 清單取代 semantic roles。
- 只列元件名稱，漏掉 variants、states 與 responsive behavior。
- 把一次性頁面 composition 過度抽象成共用元件。
- 忽略既有 token/component，另建一套平行 design system。
