# DOTS / Job System / Burst：何時值得

Unity 的 DOTS（Data-Oriented Technology Stack）能讓「上萬個實體」跑得動，但它是**另一套程式模型**，遷移成本高。這篇是「值不值得、怎麼漸進採用」的決策——game-dev 的 data-oriented-layout（AoS/SoA、cache）與 data-ecs-pattern（ECS 何時用）是引擎中立原則，這篇是 Unity 落地與取捨。

## 三件套可以分開用（關鍵認知）

DOTS 常被當成「全有或全無」，其實是三個**可獨立採用**的東西，成本遞增：

| 元件 | 是什麼 | 遷移成本 | 單獨用的價值 |
|------|--------|---------|------------|
| **Burst** | 把 C# 編譯成高度優化的原生碼 | 低（標記 + 限制寫法） | 數學密集函式直接快數倍 |
| **Job System** | 多執行緒安全地跑工作 | 中（改成 struct job、無托管型別） | 把重運算分到多核，不卡主線 |
| **ECS**（Entities） | 資料導向的實體架構（取代 GameObject/MonoBehaviour） | **高**（整個架構換掉） | 大量同型實體的 cache 效率 + 批次 |

**採用順序按成本**：先 Burst（幾乎白拿）、再 Job System（重運算並行化）、最後才 ECS（架構級決定）。**多數專案止步於 Burst + Job，不需要完整 ECS**。

## Burst：最低成本的加速

```csharp
[BurstCompile]
public struct SteeringJob : IJobParallelFor
{
    [ReadOnly] public NativeArray<float3> positions;
    public NativeArray<float3> velocities;
    public void Execute(int i) { /* 純數學：Burst 編譯後快數倍 */ }
}
```

- **適合**：向量/物理/尋路等數學密集的熱迴圈（見 game-dev algo-physics）。
- **限制**：Burst 函式內不能用托管型別（class、string、大部分 Unity API）——只能 struct + NativeContainer + 數學。所以通常跟 Job System 一起用。
- **性價比最高**：把熱路徑的純運算包成 Burst job，改動局部、收益明顯。

## Job System：並行化重運算

- **適合**：可平行、大量同型的運算（上千單位的 steering、粒子、格點模擬）——分到多核，不卡主執行緒（對應 game-dev perf-optimization-playbook 的背景執行緒，但 Job 是結構化安全版）。
- **NativeContainer**：Job 只能碰 `NativeArray` 等——資料要先從托管世界搬進 native，算完搬回，這個來回有成本，小量資料不划算。
- **安全系統**：Job System 靠 struct + 依賴排程避免 race——編譯器擋掉大部分並行 bug（比手開 thread 安全，見 game-dev net-server 的共用模擬層並行地獄）。
- **排程與依賴**：`job.Schedule()` 回 handle，用 `JobHandle` 串依賴——別在同幀 `Complete()` 立刻等（等於沒並行），排下去讓它跑、下一個需要結果的點才 Complete。

## ECS（Entities）：架構級決定

- **適合**：**大量、同型、每幀更新**的實體（彈幕、RTS 千單位、大規模模擬）——ECS 的 component 連續存放（SoA，見 game-dev data-oriented-layout）+ system 批次掃過，cache 效率碾壓 GameObject。
- **成本極高**：整個架構換掉——不是 MonoBehaviour、不是 GetComponent、不是 Instantiate。團隊要重學，工具鏈（Inspector、除錯）較弱，與傳統 GameObject 世界的橋接（混合）要額外處理。
- **何時真的值得**：對照 game-dev data-ecs-pattern 的「何時用/不用」——**大量同型實體且已量測到 GameObject 撐不住**才上；少量、高度客製、關係複雜的東西 ECS 反而礙事。
- **混合現實**：多數用 ECS 的專案是**局部**用（大量實體的子系統走 ECS，其餘 GameObject）——不是全盤 ECS。Unity 的 Baking/SubScene 做橋接。

## 決策流程

1. **先量測**（見 `perf-profiling.md`）——確認瓶頸真的在 CPU 的大量同型運算，不是 GC、不是渲染、不是別的。
2. **能不能用便宜手段解**：物件池、降頻、空間分割（game-dev perf-optimization-playbook 的少做事）往往就夠——別為了「聽起來高級」上 DOTS。
3. **數學熱點** → Burst（+ Job）。
4. **大量可平行運算** → Job System。
5. **上萬同型實體且上述都不夠** → 才考慮 ECS，且評估遷移成本 vs 收益。

## 常見坑

- **為了高級感上 ECS**：沒量測、實體沒那麼多、或問題根本是 GC/渲染——DOTS 解決不了，還付出巨大遷移成本。先量測、先試便宜手段。
- **當成全有全無**：以為要 DOTS 就得全 ECS——Burst/Job 可以單獨拿，先摘低垂果實。
- **Job 立刻 Complete**：`Schedule()` 後同幀馬上 `Complete()` 等結果 = 沒有並行——排下去，延到真需要才等。
- **NativeContainer 洩漏**：`NativeArray` 要 `Dispose()`（或用 `Allocator.TempJob`/`Temp` 自動）——忘了 dispose 是 native 記憶體洩漏，Unity 會警告。
- **小資料丟 Job**：托管↔native 來回成本超過並行收益——Job 給夠大的批量才划算。
- **ECS 與 GameObject 硬橋接**：大量跨界同步（ECS 實體 ↔ GameObject）成本高——橋接點要少而明確。
