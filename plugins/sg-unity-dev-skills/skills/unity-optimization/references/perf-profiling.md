# Unity 效能量測（Profiler 工具鏈）

game-dev 的 game-tooling perf 講「先量測再優化、幀預算、spike vs 均值」（引擎中立方法論）；這篇是那套方法在 Unity 的**工具落地**——用哪個工具、怎麼判讀、怎麼避免量出假數據。

## 三個工具各管什麼

| 工具 | 回答 | 何時開 |
|------|------|--------|
| **Profiler**（CPU/GPU/Memory 時間軸） | 這幀時間花在哪、哪個系統/函式重、GC 何時觸發 | 掉幀、卡頓的第一站 |
| **Frame Debugger** | 這幀畫了幾個 DrawCall、每個畫什麼、為什麼沒合批 | 渲染重、DrawCall 多時（見 `perf-rendering.md`） |
| **Memory Profiler**（套件） | 記憶體被什麼佔、洩漏、重複資產 | 記憶體漲、OOM、載入分析（見 `../../unity-scripting/references/asset-loading.md`） |

## Profiler 判讀紀律

- **先分 CPU vs GPU**：Profiler 看誰是瓶頸——CPU bound（邏輯/GC 重）與 GPU bound（渲染重）的解法完全不同（對應 game-tooling 的 CPU/GPU 分野）。
- **spike 看時間軸不看平均**：規律尖刺多半是 GC（見 `perf-gc-and-memory.md`）；不規律大尖刺是載入、實例化、首次使用——Profiler 逐幀看最差幀，別被平均值騙（game-tooling 的 spike vs 均值）。
- **GC Alloc 欄是重點**：Profiler 的 CPU 模組看每幀 `GC Alloc`——**穩態下應趨近零**，非零就是每幀在配置（找來源見 gc 篇）。
- **展開找熱點**：Hierarchy/Timeline 視圖展開，找佔比最大的——別在 0.05ms 的函式上浪費一天（game-tooling 的量級對症）。

## 量測的假數據陷阱（Unity 專屬）

- **Editor 裡量不準**：Editor 有額外開銷（Editor loop、Gizmos、Scene view）——**量測要用 Development Build 在目標裝置**跑，Editor 只能看結構不能當結論。
- **Deep Profile 會扭曲**：Deep Profile 記錄每個函式呼叫，開銷巨大、時間分佈失真——先用一般 Profiler 找方向，只對嫌疑區開 Deep 或手動 `ProfilerMarker`。
- **首次執行不算**：第一次進場景有 shader 編譯、JIT/首次實例化——量穩態要跑幾秒後再看。
- **Vsync/目標幀率**：開著 Vsync 量出來的幀時間被鎖住看不出真實負載——量測時關 Vsync 看實際 ms。

## 常駐計時（配合遊戲內面板）

Profiler 之外，遊戲內放輕量計時（`ProfilerMarker` + 螢幕面板）——對應 game-tooling 的常駐計時面板，效能退化當天可見而非三週後：

```csharp
static readonly ProfilerMarker s_aiMarker = new("AI.Update");
void UpdateAI() { using (s_aiMarker.Auto()) { /* ... */ } }
```

## 目標裝置

**在最弱目標裝置量測**（見 game-tooling measurement-first）——桌機跑 200fps 對手機毫無意義。手機、掌機的瓶頸（頻寬、發熱降頻、GPU）與桌機完全不同。

## 常見坑

- **在 Editor / 非 Development Build 量**：數字與出貨版差很多。
- **開 Deep Profile 當常態**：扭曲時間分佈。
- **只看平均幀率**：spike 被平均掉，玩家最有感的卡頓看不見。
- **量一次就下結論**：熱機、背景程序、首次執行都影響——多次取中位數。
- **憑感覺鎖定嫌疑犯**：「一定是尋路慢」——量下去是每幀字串拼接。感覺只決定先量哪，不決定改哪。
