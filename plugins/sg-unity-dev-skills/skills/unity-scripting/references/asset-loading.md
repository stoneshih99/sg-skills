# 資產載入：Addressables / Resources / 直接參照

Unity 有多種載資產的方式，選錯的代價是記憶體爆、載入卡頓、或包體膨脹。這篇是選型與生命週期紀律。game-dev 的 system-foundation（資源 handle + 引用計數）與 perf-common-hotspots（載入 spike）是引擎中立原則，這篇是 Unity 落地。

## 三種載入方式選型

| 方式 | 是什麼 | 適合 | 痛點 |
|------|--------|------|------|
| **直接參照**（SerializeField） | Inspector 拉、隨場景/prefab 載入 | 該物件必用、數量固定的資產 | 一被引用就跟著進記憶體，無法動態卸載 |
| **Resources 資料夾** | `Resources.Load(path)` 字串載入 | 快速原型、極少量全域資產 | **全進包**（Resources 內容全部打進建置且常駐分析）、字串路徑脆、官方不建議大用 |
| **Addressables** | 位址化非同步載入 + 引用計數 | **正式專案的預設** | 需設定與學習；要管 handle 釋放 |

**建議**：正式專案用 **Addressables**——非同步（不卡主線）、引用計數自動管記憶體、可遠端更新（熱更）、可分析依賴。`Resources` 只留給極少數「原型期、量小、確定常駐」的東西。直接參照給「數量固定、必用」的。

```csharp
// Addressables：非同步 + 可取消 + 記得釋放
async UniTask<GameObject> SpawnEnemyAsync(string key, CancellationToken ct)
{
    var handle = Addressables.LoadAssetAsync<GameObject>(key);
    var prefab = await handle.ToUniTask(cancellationToken: ct);
    var go = Instantiate(prefab);
    // handle 要在不再需要時 Addressables.Release(handle)——引用計數歸零才卸載
    return go;
}
```

## 生命週期：載了要釋放

- **Addressables 是引用計數**：`LoadAssetAsync` +1、`Release` -1，歸零才真的卸載。**load/release 要配對**——只 load 不 release 是記憶體只增不減（對應 game-dev system-foundation 的 handle 引用計數）。
- **綁生命週期釋放**：場景域資產綁場景（切場景時 ReleaseInstance/Release 整批）——手動配對在場景切換時必漏，用「域」兜底（見 game-dev system-scene 的場景域資源）。
- **Instantiate vs InstantiateAsync**：Addressables 的 `InstantiateAsync` 會自動追蹤，`ReleaseInstance` 一併處理載入計數——比自己管 handle + Instantiate 少漏。

## 同步 vs 非同步

- **遊玩中一律非同步**（見 game-dev perf-common-hotspots 的載入 spike）——同步載入大資產卡主線幾百 ms。
- **載入畫面內可同步**：載入畫面本來就是等待節點。
- **非同步回來要檢查存活**：載入期間需求可能消失（怪還沒載完就清場）——用取消 token 綁生命週期（見 `script-async.md`）。

## 記憶體現實

- **貼圖是記憶體大頭**：載入分析要盯貼圖（見 `../../unity-optimization/references/perf-profiling.md` 的 Memory Profiler）；壓縮格式與尺寸在匯入期定（見 `asset-import-pipeline.md`）。
- **Resources 常駐分析**：Resources 資料夾內容影響啟動記憶體與建置分析——大資產別放 Resources。
- **依賴重複**：多個 Addressables group 引用同一資產可能重複打包——用依賴分析（Analyze 工具）抓。

## 常見坑

- **只 load 不 release**：記憶體只增不減——load/release 配對，或用場景域兜底。
- **大量資產塞 Resources**：全進包、常駐、啟動慢——正式專案用 Addressables。
- **遊玩中同步載入**：一顆技能圖示卡 200ms——遊玩中非同步 + 預載。
- **非同步回來物件已死**：載完 Instantiate 到已卸載的場景——取消 token 綁生命週期。
- **字串路徑硬編碼**（Resources/Addressables key）：打錯無編譯期檢查、改名全斷——集中管理 key 或用 AssetReference（Addressables 的型別化參照）。
