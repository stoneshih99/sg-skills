# GC Alloc 與記憶體

Unity（Mono/IL2CPP）的 GC 是**非分代、會 stop-the-world** 的——每幀配置累積到觸發 GC 時，畫面就是一個規律尖刺。消除每幀 GC Alloc 是 Unity 效能的核心功課之一。game-dev perf-common-hotspots 的「每幀配置/GC」是引擎中立診斷，這篇是 Unity 專屬來源與消除法。

## 目標：穩態下每幀 GC Alloc = 0

Profiler 的 CPU 模組 `GC Alloc` 欄（見 `perf-profiling.md`）在穩態下應趨近零。非零就逐項揪來源：

## 常見 GC Alloc 來源（Unity 專屬）

| 來源 | 例 | 消除 |
|------|-----|------|
| **每幀 new** | `new List<>()`、`new Vector3[]` 在 Update | 預先配置、重用緩衝 |
| **字串** | `"Score: " + score`、`string.Format` 每幀 | 只在值變才更新、`StringBuilder`、TextMeshPro 的 SetText(數字) |
| **裝箱（boxing）** | value type 塞進 object/介面、`enum` 當 Dictionary key | 泛型、`enum` 用 `IEqualityComparer` |
| **閉包 / lambda 捕獲** | Update 裡的 lambda 捕獲區域變數 | 提成方法、快取 delegate |
| **foreach 某些集合** | 舊版對某些集合 foreach 配置 enumerator | for 迴圈、或用官方無配置版本 |
| **Unity API 回傳陣列** | `GetComponents()`、`Physics.RaycastAll`、`Mesh.vertices` | 用 NonAlloc 版（`RaycastNonAlloc`）、快取 mesh 資料 |
| **裝箱的 params** | `Debug.Log` 字串拼接、`string.Format` | 條件編譯移除 log、少在熱路徑 log |

```csharp
// 錯：每幀配置 + 字串
void Update() { label.text = "HP: " + hp; }

// 對：值變才更新（髒標記，對應 game-tooling 的 dirty flag）
int _lastHp = -1;
void Update() {
    if (hp != _lastHp) { label.SetText("HP: {0}", hp); _lastHp = hp; }
}

// 物理查詢用 NonAlloc
readonly RaycastHit[] _hits = new RaycastHit[16];
int n = Physics.RaycastNonAlloc(ray, _hits, dist);
```

## 物件池（Unity 落地）

頻繁 Instantiate/Destroy（子彈、粒子、傷害數字、敵人）是 GC spike 的頭號來源——用池（見 game-dev perf-optimization-playbook 的池化 + system-scene 的池預熱）：

- Unity 2021+ 內建 `ObjectPool<T>`；或自寫。
- **停用而非銷毀**：`SetActive(false)` 回池、`SetActive(true)` 取出重置——重置要徹底（清速度、清狀態、重設 transform）。
- **預熱到峰值**：最吵場景的同時數就是池容量，載入期填滿——執行期擴池反而 spike。
- Addressables 的 instance 也要走池思維（見 `../../unity-scripting/references/asset-loading.md`）。

## GC 策略

- **Incremental GC**（Player Settings）：把一次大停頓拆成多幀小停頓——減少單幀 spike，但總開銷略增。先消 alloc，再靠它兜底。
- **IL2CPP vs Mono**：出貨用 IL2CPP（更快、AOT）——但 GC 行為仍在，不是免死金牌。
- **手動 GC.Collect**：只在明確的「載入畫面、關卡切換」這種可接受停頓的點呼叫，不要在遊玩中。

## 記憶體（非 GC）

- **貼圖是大頭**：Memory Profiler 抓佔用，壓縮/尺寸在匯入定（見 `../../unity-scripting/references/asset-import-pipeline.md`、game-dev art-tech-specs）。
- **洩漏偵測**：Memory Profiler 兩次快照 diff——該卸的沒卸（未 Release 的 Addressables、未退訂的事件持有物件）。
- **場景卸載不乾淨**：殘留的訂閱、靜態參照、SO 持有的回呼——見 `../../unity-scripting/references/script-architecture-glue.md` 與 game-dev system-scene。

## 常見坑

- **字串每幀拼**：UI 數值刷新最常見——髒標記 + SetText。
- **RaycastAll / GetComponents 熱路徑**：回傳陣列每次配置——NonAlloc 版 + 預配置緩衝。
- **裝箱藏在 enum key**：`Dictionary<MyEnum, T>` 在舊 runtime 裝箱——給 comparer。
- **池重置不徹底**：取出的物件帶著上次的速度/狀態——重置清乾淨。
- **先上 Incremental GC 而不先消 alloc**：治標——alloc 消到零才是根治。
