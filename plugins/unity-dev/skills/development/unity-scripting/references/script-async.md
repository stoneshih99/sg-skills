# 非同步：Coroutine / UniTask / Awaitable

Unity 的非同步有三條路，選錯的代價是記憶體洩漏、幽靈回呼、難追的時序 bug。這篇是選型 + 取消/生命週期綁定的紀律。

## 三者選型

| 方案 | 本質 | 適合 | 痛點 |
|------|------|------|------|
| **Coroutine** | `IEnumerator` + `yield`，綁 MonoBehaviour | 簡單時序（等幾秒、等一幀、簡單序列） | 無回傳值、無例外傳播、無法 await、宿主停用就默默停 |
| **UniTask** | 零配置的 async/await（第三方，Cysharp） | 幾乎所有非同步：載入、序列、並行、有回傳值 | 需引入套件；要懂 CancellationToken |
| **Awaitable** | Unity 內建的 async/await（2023+） | 官方原生、不想加套件時 | 生態與功能仍不及 UniTask 成熟 |

**建議**：新專案用 **UniTask**（回傳值、例外、並行組合、幾乎零 GC——見 `../../unity-optimization/references/perf-gc-and-memory.md`；一般 async/await 在 Unity 會配置）；不想加套件且 Unity 夠新用 **Awaitable**；Coroutine 只留給「等 X 秒」這種一次性簡單時序。**專案內統一一種**，混用是維護災難。

```csharp
// UniTask：有回傳、可取消、可組合
async UniTask<Texture> LoadIconAsync(string id, CancellationToken ct)
{
    var handle = Addressables.LoadAssetAsync<Texture>(id);
    return await handle.ToUniTask(cancellationToken: ct);
}

// 並行等多個
await UniTask.WhenAll(LoadA(ct), LoadB(ct));
```

## 取消：非同步的第一紀律

**每個非同步操作都要能被取消，且取消要綁物件生命週期**——否則物件銷毀了、非同步還在跑，回來時操作已死的物件 = NullReference 或改到不該改的狀態（對應 game-dev 的 net-prediction「回來時需求已消失」）。

```csharp
// 綁到 MonoBehaviour 生命週期：物件銷毀自動取消
async UniTask DoWork()
{
    var ct = this.GetCancellationTokenOnDestroy();
    await SomeLongOp(ct);
    // 到這裡若物件已銷毀，UniTask 會拋 OperationCanceledException 中止，不會往下執行
}
```

- **Coroutine 的取消**：`StopCoroutine`/`StopAllCoroutines`，或宿主停用自動停——但「自動停」也是坑：你以為會跑完的清理沒跑。
- **await 之後檢查存活**：長操作 await 回來後，若沒用取消 token，手動 `if (this == null) return;`（Unity 的 null 是覆寫過的「已銷毀」判定）。

## 常見坑

- **一般 `async void`**：例外被吞、無法 await、無法取消——除了事件處理器外禁用；UniTask 用 `UniTaskVoid` 明確表達。
- **await 後用了舊狀態**：await 期間世界變了（物件移動、狀態改變），回來用 await 前的快照——長操作要重新讀當前狀態或改用快照設計。
- **Coroutine 宿主停用默默中止**：把重要清理放協程尾端，宿主一停就永遠不執行。清理走 OnDisable，不放協程尾。
- **忘了取消 = 洩漏**：載入場景切換了、非同步還握著資源不放——取消 token 綁場景/物件生命週期是防洩漏的根本（見 `asset-loading.md` 的載入取消）。
- **每幀 await 的開銷**：`await UniTask.Yield()` 每幀雖輕，大量並行仍有成本；高頻迴圈評估是否真需要非同步。

## 與 game-dev 的關係

時序與取消的**架構原則**（決策與執行分離、狀態快照）見 game-dev-skills 的 `system-foundation`（事件與生命週期）與 `data-separation`；這篇是那些原則在 Unity 三種非同步機制上的落地。
