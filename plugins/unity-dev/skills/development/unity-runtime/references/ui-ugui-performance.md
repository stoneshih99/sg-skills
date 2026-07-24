# uGUI 效能：Canvas rebuild 與 Raycast

uGUI 慢的兩大來源：Canvas rebuild（一個元素變動重建整個 Canvas 網格）和 Raycast Target 掃描。這篇含一個吃掉世界點擊、卻不報錯的坑。

## Canvas 分割：rebuild 的核心

**一個 Canvas 是一個 batch 單位——Canvas 內任何一個元素變動（文字、位置、顏色），整個 Canvas 的網格重建（rebuild/rebatch）**。所以：

- **動態與靜態分開 Canvas**：每幀跳的傷害數字、計時器、血條 → 放**自己的 Canvas**；靜態 HUD 背景 → 另一個 Canvas。別讓一個每幀變的計時器拖著整個 HUD rebuild（對應 game-dev ui-tech-specs 的動靜分離）。
- **巢狀 Canvas 隔離 rebuild**：子 Canvas 的 rebuild 不波及父——高頻變動區塊用子 Canvas 圈起來。
- **診斷**：Profiler 的 UI 模組 / `Canvas.BuildBatch`、`Canvas.SendWillRenderCanvases` 時間——高就是 rebuild 頻繁。

## 每幀更新用髒標記

- **值沒變不 SetText / 不改**：`if (hp != _last)` 才更新（見 `../../unity-optimization/references/perf-gc-and-memory.md` 的字串 + game-tooling dirty flag）——每幀無條件 set 是 rebuild + GC 雙重罪。
- **用 CanvasGroup.alpha 而非逐個改**：整組淡入淡出用 CanvasGroup，不要遍歷每個元素改 color。
- **隱藏用 SetActive / CanvasGroup**：關掉的 UI 若還在排版更新就白付——真正停用（見 game-dev system-ui 「隱藏 ≠ 停用」）。

## 坑：Raycast Target 吃掉世界點擊

**uGUI 的 `Graphic`（Text / Image）預設 `Raycast Target = true`**——它們會參與 UI 射線檢測。兩個後果：

1. **效能**：每個 Raycast Target 都進 EventSystem 的射線掃描，滿屏純顯示文字/圖拖慢點擊檢測。
2. **正確性（陰險）**：若你用 `EventSystem.current.IsPointerOverGameObject()` 判斷「世界點擊有沒有被 UI 擋住」，任何疊在遊戲畫面上、**純顯示用**的文字/圖（HUD、狀態列）只要沒關 Raycast Target，就會**靜默吃掉底下的世界點擊**——玩家點世界沒反應，**且沒有任何錯誤訊息**。

**解法**：**所有純顯示、不需互動的 Graphic 關掉 Raycast Target**（HUD 文字、裝飾圖、血條底圖）。只有真的要接點擊的（按鈕、可拖曳區）才留 true。這也順帶減少射線掃描負擔——一舉兩得。

## 其他 uGUI 效能點

- **Layout Group 昂貴**：`Vertical/HorizontalLayoutGroup` + `ContentSizeFitter` 每次變動重算佈局——大量元素（長列表）用**物件池 + 手動佈局**或虛擬化清單，別讓 Layout Group 管上百個。
- **Overdraw**：滿版半透明面板、大量疊圖（見 `../../unity-optimization/references/perf-rendering.md` overdraw）——不透明區用不透明、裁掉看不見的。
- **圖集**：UI sprite 進圖集（`../../unity-scripting/references/asset-import-pipeline.md` 的 spritePackingTag）減 DrawCall。
- **TextMeshPro**：取代預設 Text（品質 + 效能）。

## 常見坑

- **Raycast Target 全開**：純顯示元素靜默吃世界點擊、拖慢射線——顯示用的一律關。
- **一個 Canvas 裝所有東西**：一個計時器變動 rebuild 全 HUD——動靜分 Canvas。
- **每幀 SetText**：rebuild + GC——髒標記。
- **Layout Group 管長列表**：每次變動重算——池化 + 虛擬化。
- **隱藏用 alpha=0 卻仍更新**：看不見還在付成本——CanvasGroup 或 SetActive 真停用。
