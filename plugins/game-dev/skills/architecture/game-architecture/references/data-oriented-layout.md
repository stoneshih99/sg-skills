# 資料導向記憶體佈局

資料與行為分離後，最大的效能紅利來自**怎麼在記憶體裡排資料**。CPU 讀記憶體是以 cache line 為單位一次抓一串；資料排得連續、只放需要的欄位，就能餵飽 cache，批次處理才快。

## 為什麼佈局決定速度

- **Cache locality**：CPU 一次載入一整條 cache line（常見 64 bytes）。若下一筆要用的資料就在旁邊，等於免費；若散在各處，每次都 cache miss，等記憶體的時間遠大於運算本身。
- **每幀熱路徑**：每幀對上萬個物件做同一件事時，記憶體存取模式比演算法常數還關鍵。

## AoS vs SoA

**AoS（Array of Structs）**：一個陣列，每個元素是完整結構。

```
struct Particle: position, velocity, color, lifetime
particles: Array<Particle>       # [p0.pos,p0.vel,p0.col,p0.life, p1.pos,...]
```

- 直覺、單一物件存取方便。
- 但只更新 position 時，velocity/color/lifetime 也被一起載進 cache——浪費頻寬。

**SoA（Struct of Arrays）**：每個欄位各自一個連續陣列。

```
positions:  Array<Vec>
velocities: Array<Vec>
colors:     Array<Color>
lifetimes:  Array<float>
```

- 只跑 position += velocity 時，只掃 positions 與 velocities 兩條連續陣列，cache 全部命中，且對 SIMD 友善。
- 代價：存取「單一粒子的所有欄位」較不方便，欄位增減要動多個陣列。

```
# SoA 的批次更新：兩條連續陣列線性掃過
function integrate(positions, velocities, dt, count):
    for i in 0..count:
        positions[i] += velocities[i] * dt
```

**選擇**：以「哪些欄位常一起被存取」分組。整批只碰少數欄位 → SoA；常需要單一物件的完整資料 → AoS 或混合（把常一起用的欄位打包成一個 struct，再對這些 struct 做 SoA）。

## 批次處理（Batch Processing）

把「對每個物件做一次」改成「對一整批做一輪」：

- 同型資料連續擺放 → 一個系統一次線性掃完。
- 分支盡量移出內迴圈（先依狀態分堆，再各自批次處理），減少分支預測失敗。
- 一次遍歷做完一組相關運算，別為每個小操作各掃一遍。

## 冷熱資料切分（Hot/Cold Splitting）

把「每幀都碰」的熱欄位和「很少碰」的冷欄位拆開存：

```
# 熱：每幀更新
struct EnemyHot: position, velocity, hp
# 冷：偶爾才用（顯示名稱、掉落表、對話 id）
struct EnemyCold: displayName, lootTableId, dialogueId
```

熱資料更密、更多筆塞進同一條 cache line，熱迴圈更快；冷資料另放，用同一索引對應。

## 遊戲情境

- 粒子系統、彈幕、boids、大量 AI：SoA + 批次更新。
- ECS 的 component 儲存（見 `data-ecs-pattern.md`）通常就是每種 component 一條連續陣列（SoA 精神）。
- 物件池 + 連續陣列：避免每幀配置、維持局部性。

## 陷阱

- **過早優化**：只有大量、每幀、且已量測到是瓶頸的熱路徑才值得 SoA / 冷熱切分；小規模用 AoS 更好維護。
- **假設佈局，不量測**：cache 行為反直覺，一定要 profiler 實測，別憑感覺。
- **SoA 索引不同步**：多條陣列用同一索引對應同一物件，新增 / 刪除（尤其 swap-and-pop）必須同時對所有陣列做，否則欄位錯位。
- **指標打散局部性**：熱結構裡塞指向別處的參照，等於每筆都跳一次記憶體，抵銷連續佈局的好處。
