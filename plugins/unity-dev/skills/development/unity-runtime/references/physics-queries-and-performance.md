# 物理查詢與效能

Raycast/Overlap 這類物理查詢是遊戲的命中判定、視線、範圍偵測核心（game-dev algo-physics 的 raycast、system-action-combat 的 hitbox 即時查詢），但用錯會 GC 爆炸或效能拖垮。這篇是 Unity 物理查詢的正確用法與效能。

## 查詢類型

| 查詢 | 用途 |
|------|------|
| `Raycast` | 射線命中最近的（射擊、視線、地面偵測，見 game-dev algo-physics） |
| `SphereCast` / `BoxCast` / `CapsuleCast` | 掃掠：有粗細的射線（角色移動掃掠、粗準星） |
| `OverlapSphere` / `OverlapBox` | 範圍內所有碰撞體（爆炸範圍、AOE、即時 hitbox 查詢，見 system-action-combat 模式 B） |

## GC 坑：用 NonAlloc 版

**`RaycastAll`、`OverlapSphere` 回傳陣列——每次呼叫配置新陣列 → 每幀查詢就是每幀 GC Alloc**（見 `../../unity-optimization/references/perf-gc-and-memory.md` 的 Unity API 回傳陣列）：

```csharp
// 錯：每幀配置
RaycastHit[] hits = Physics.RaycastAll(ray, dist);

// 對：預配置緩衝，NonAlloc 填入
readonly RaycastHit[] _hits = new RaycastHit[16];
int n = Physics.RaycastNonAlloc(ray, _hits, dist, _layerMask);
for (int i = 0; i < n; i++) { /* _hits[i] */ }
```

- **熱路徑的查詢一律 NonAlloc 版**（`RaycastNonAlloc`、`OverlapSphereNonAlloc`）+ 預配置緩衝。
- 緩衝要夠大（超過的被丟棄，回傳值 = 實際填入數，可能等於緩衝上限代表可能有漏）。
- 新的 `Physics.RaycastCommand`（Job/Burst 批次查詢）給大量查詢——上千條射線用它（見 `../../unity-optimization/references/perf-dots.md`）。

## LayerMask：查詢的第一道剪枝

- **查詢帶 LayerMask**——只測相關的層，不是全場：`Physics.Raycast(ray, out hit, dist, layerMask)`。
- 建 mask：`LayerMask.GetMask("Enemy", "Wall")` 或位元運算——**別讓查詢掃到不相關的層**（子彈的射線不用測 UI 層、拾取層）。
- 這是效能與正確性雙贏：省計算 + 不誤命中（對應 game-dev algo-data-structures 空間分割的粗篩、system-action-combat 的條件剪枝）。

## QueryTriggerInteraction

- 查詢預設會不會打中 Trigger 碰撞體由全域設定決定——**明確指定** `QueryTriggerInteraction.Ignore`/`Collide`，別靠全域預設（射擊要穿過觸發區還是被擋，是設計決策）。

## 效能：碰撞與查詢

- **碰撞對數爆炸**：N 個動態碰撞體兩兩檢測是 O(n²)（game-dev algo-data-structures 的碰撞對）——層矩陣過濾（見 `physics-rigidbody-and-collision.md`）、大量物件考慮自己做空間分割 + raycast 取代物理碰撞。
- **靜態碰撞體別動**：移動無 Rigidbody 的 Collider 重建靜態樹（見 rigidbody 篇）——會動就給 Rigidbody（標 kinematic）。
- **Sleep**：靜止的動態 Rigidbody 會自動 sleep（不再算）——別用微小力持續戳醒它們。
- **碰撞體用原始形狀**：Box/Sphere/Capsule 便宜，Mesh Collider 貴（尤其非 convex）——精細形狀只給需要的（game-dev algo-physics 用原始形狀近似）。
- **降低 Fixed Timestep 頻率**（若物理不需高精度）：`Time.fixedDeltaTime` 調大減少物理步——但影響手感與穿隧，權衡。

## 常見坑

- **RaycastAll/OverlapSphere 熱路徑**：每幀配置陣列——NonAlloc + 預配置緩衝。
- **查詢不帶 LayerMask**：掃全場、誤命中——一律帶 mask。
- **Mesh Collider 滿場**：物理巨慢——原始形狀近似。
- **移動靜態碰撞體**：重建靜態樹——給 Rigidbody。
- **NonAlloc 緩衝太小**：結果被截斷、漏命中——緩衝夠大且檢查是否填滿。
- **靠全域 QueryTriggerInteraction**：行為隨全域設定變——每個查詢明確指定。
