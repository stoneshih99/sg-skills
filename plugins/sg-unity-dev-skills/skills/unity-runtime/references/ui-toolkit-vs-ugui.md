# uGUI vs UI Toolkit 選型

Unity 有兩套 UI 系統並存，選錯的代價是做到一半發現缺功能。這篇是選型。UI 的**程式架構**（畫面堆疊、MVVM、指令回流）是引擎中立的，見 game-dev 的 system-ui；這篇只管「Unity 用哪套、怎麼落地」。

## 兩套的定位

| | uGUI（Unity UI，GameObject-based） | UI Toolkit（UXML/USS，retained-mode） |
|--|-----------------------------------|--------------------------------------|
| 本質 | Canvas + GameObject + Component | 類 web（UXML 結構 + USS 樣式 + C#） |
| 成熟度 | 極成熟、生態/資源多、所有版本支援 | 較新、執行期 UI 仍在補功能 |
| 世界空間 UI | **原生支援**（血條、3D 選單、diegetic） | 執行期世界空間支援弱/受限 |
| 大量元素效能 | Canvas rebuild 是痛點（見 `ui-ugui-performance.md`） | retained-mode，大量元素較省 |
| 樣式重用 | prefab + 手動 | **USS 樣式表**，類 CSS 重用 |
| 編輯器工具 UI | 可但不理想 | **官方推薦**（見 `../../unity-scripting/references/editor-tools.md`） |
| 資料綁定 | 手動 | 內建 binding（新版強化中） |

## 選型準則

- **編輯器工具 UI** → **UI Toolkit**（官方方向、樣式與佈局好維護）。
- **遊戲執行期 UI，需要世界空間**（血條、3D 互動、diegetic HUD，見 game-dev ui-hud-and-menus 的 diegetic）→ **uGUI**（世界空間原生）。
- **遊戲執行期 UI，純螢幕空間 + 資料密集 + 大量元素**（背包、排行、複雜選單）→ UI Toolkit 值得評估（效能與樣式優勢），但先確認你需要的執行期功能它都有。
- **求穩、資源多、團隊熟** → uGUI 仍是最保險的執行期選擇。
- **混用**：常見「遊戲內 HUD/世界空間用 uGUI、編輯器工具用 UI Toolkit」——兩套並存沒問題，按場景選。

## 落地紀律（兩套共通）

- **架構分層照 game-dev system-ui**：畫面管理器（堆疊 + 層級）、UI 讀投影不讀本體、改狀態走指令、事件驅動更新——這些是引擎中立原則，兩套 UI 都適用。
- **文字不進圖**：本地化（見 game-dev loc-*）——uGUI 用 TextMeshPro、UI Toolkit 用 Label，都走字串表不嵌圖。
- **效能**：uGUI 看 `ui-ugui-performance.md`（Canvas rebuild、Raycast Target）；UI Toolkit 看元素數與樣式複雜度。

## 常見坑

- **做到一半發現缺功能**：UI Toolkit 執行期的某功能（世界空間、特定互動）不成熟——**開工前確認你要的執行期功能它都有**。
- **一個專案硬用一套**：編輯器工具硬用 uGUI、世界空間 UI 硬用 UI Toolkit——按場景選，混用是常態。
- **忽略架構層**：糾結選哪套 UI，卻把遊戲邏輯寫進 UI 腳本——選型是小事，UI 與邏輯解耦（system-ui）才是大事。
- **TextMeshPro 沒用**：uGUI 預設 Text 品質差——一律 TextMeshPro。
