---
name: unity-optimization
description: Unity 效能與建置的實作決策與坑——兩家族：效能（Profiler/Frame Debugger 判讀、GC Alloc 與物件池、DrawCall/Batching、DOTS/Job/Burst 何時值得）、建置（命令列 build/CI、IL2CPP vs Mono 與 AOT 坑、平台差異與條件編譯）。當遊戲很卡要找瓶頸、消 GC、優化渲染、評估 DOTS，或出 build、設 CI、build 崩/IL2CPP/AOT 問題、做多平台時使用。引擎中立量測方法論見 sg-game-dev-skills；寫 code 見 unity-scripting、執行期系統見 unity-runtime。含 C#。
---

# Unity 效能與建置（Unity Optimization）

> **定位**：Unity **效能優化與建置出貨**的實作決策與坑。寫 code 見 `unity-scripting`；執行期系統見 `unity-runtime`；引擎中立的量測方法論、優化手法選型、發佈流程見 **sg-game-dev-skills**（game-tooling / game-production）——本 hub 是「在 Unity 裡怎麼量、怎麼優化、怎麼出 build」。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 掉幀/卡頓/記憶體：Profiler、GC、渲染、DOTS | 效能 | ↓ Perf |
| 出 build、CI、IL2CPP、平台差異 | 建置 | ↓ Build |

貫穿鐵律：**先量測再優化**（見 `references/perf-profiling.md`）；**Mono 開發、IL2CPP 出貨的一定要在 IL2CPP build 實測**（見 `references/build-il2cpp.md`）。

## Perf（效能）

| 何時 | 讀 |
|------|-----|
| Profiler / Frame Debugger / Memory Profiler 判讀、量測紀律 | `references/perf-profiling.md` |
| GC Alloc 來源與消除、物件池 | `references/perf-gc-and-memory.md` |
| DrawCall/SetPass、Batching 四法、Overdraw | `references/perf-rendering.md` |
| DOTS / Job System / Burst 何時值得、三件套取捨與遷移成本 | `references/perf-dots.md` |

## Build（建置與平台）

| 何時 | 讀 |
|------|-----|
| 命令列 BatchMode build、CI、開發 vs 發佈設定、build 驗證 | `references/build-command-line.md` |
| IL2CPP vs Mono、AOT 坑（反射剝離、泛型爆炸） | `references/build-il2cpp.md` |
| 平台差異、條件編譯、Player Settings、多平台矩陣 | `references/build-platform.md` |
