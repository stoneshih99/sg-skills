# 渲染效能：DrawCall / Batching / Overdraw

GPU bound（降解析度就變快）時，戰場多半在 DrawCall 數與 overdraw。這篇是 Unity 的批次手段選型與渲染熱點。game-dev perf-common-hotspots 的渲染段是引擎中立診斷，這篇是 Unity 落地。

## 先量：Frame Debugger

DrawCall 問題的第一站是 Frame Debugger（見 `perf-profiling.md`）——它逐個列出這幀的每個 draw、為什麼**沒**合批（"Objects have different materials"）。**先看它說為什麼沒合批，再選手段**，別憑感覺。

## Batching 四法選型

DrawCall 高的解法是合批——四種手段，適用不同情境：

| 手段 | 合併什麼 | 適合 | 前提/限制 |
|------|---------|------|-----------|
| **Static Batching** | 靜態物件 | 不動的場景件（地形、建築） | 標 Static；增記憶體（合併 mesh） |
| **Dynamic Batching** | 小型動態 mesh | 大量小物件（舊做法） | 頂點數限制、成本可能反超；SRP 下多被取代 |
| **SRP Batcher**（URP/HDRP） | 同 shader variant 的物件 | URP/HDRP 專案的預設 | 需相容 shader；合的是 shader 不是材質 |
| **GPU Instancing** | 同 mesh + 同材質的大量實例 | 大量相同物件（草、子彈、敵人） | 啟用材質的 instancing；用 `Graphics.DrawMeshInstanced` 更省 |

**選型**：URP/HDRP 專案 **SRP Batcher** 是地基（確保 shader 相容）；**大量相同物件**（草、彈幕）用 **GPU Instancing**；靜態場景 **Static Batching**；Dynamic Batching 多數情況讓 SRP Batcher/Instancing 取代。

**合批的天敵是材質切換**：不同材質打斷合批——用**圖集**（見 game-dev art-tech-specs、`../../unity-scripting/references/asset-import-pipeline.md` 的 spritePackingTag）合併貼圖、共用材質。材質數是 DrawCall 的地板。

## Overdraw：透明的隱藏殺手

- **半透明疊層反覆填色**——粒子、UI 背景、全螢幕效果疊越多，同一像素畫越多次，行動裝置頭號殺手（見 game-dev anim-vfx-tech-specs 的 overdraw、art-visual-readability）。
- **診斷**：Scene view 的 Overdraw 繪製模式——越亮代表疊越多。
- **對策**：減透明層、粒子貼圖裁緊（alpha 邊緣不留大片空白）、UI 不透明區塊用不透明材質、限制全螢幕效果。

## 其他 Unity 渲染熱點

- **即時光與陰影**：每盞即時光 × 每個受影響物件 = 額外 draw；即時陰影更貴——烘焙靜態光、限制即時光數（見 anim-vfx-tech-specs 「即時燈是特權」）。
- **像素負載**：高解析 + 重 fragment shader——動態解析度、shader 複雜度分級。
- **後處理**：Bloom、AO、DoF 常常一項吃掉半個 GPU 預算——逐項開關量測，砍到預算內。
- **透明排序 + 半透明 UI 全螢幕**：Canvas 全螢幕半透明是 overdraw 常客（見 `../../unity-runtime/references/ui-ugui-performance.md`）。

## 快速分診

| 症狀 | 先查 |
|------|------|
| DrawCall 數千 | 材質切換打斷合批 → Frame Debugger 看原因 → 圖集/共用材質/instancing |
| 行動裝置特別慢、降解析度就好 | overdraw → Scene view overdraw 模式 |
| 大量相同物件慢 | 沒開 GPU Instancing |
| 光影重 | 即時光/陰影數 → 烘焙 |
| 全螢幕效果重 | 後處理逐項開關 |

## 常見坑

- **沒看 Frame Debugger 就亂合批**：不知道為什麼沒合批就選手段——先看原因。
- **材質實例化打斷合批**：執行期改 `renderer.material`（複製一份材質實例）讓合批失效——用 `MaterialPropertyBlock` 改屬性不破合批。
- **UI 全螢幕半透明**：滿版透明面板 overdraw——不透明區用不透明材質。
- **即時光當免費**：每盞即時光的成本被低估——烘焙 + 限量。
- **只在強機測渲染**：目標裝置的 GPU 與頻寬完全不同（見 `perf-profiling.md` 目標裝置）。
