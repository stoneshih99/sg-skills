# Unity Test Framework：EditMode vs PlayMode

Unity Test Framework（UTF，基於 NUnit）有兩種測試模式，選錯的代價是測試慢十倍或測不到該測的東西。這篇是兩者選型與 PlayMode 的特殊性。可測性設計（怎麼讓 code 可測）見 `test-testability.md`。

## EditMode vs PlayMode 選型

| | EditMode | PlayMode |
|--|----------|----------|
| 執行環境 | 編輯器，**不進 Play**、無遊戲迴圈 | **進 Play Mode**，有真實遊戲迴圈與幀 |
| 速度 | **快**（毫秒級，無場景載入） | 慢（要進 Play、跑幀） |
| 能測 | 純邏輯、演算法、資料、Editor 工具 | MonoBehaviour 生命週期、協程、物理、場景、幀相關 |
| 適合 | **絕大多數單元測試**（純邏輯抽離後，見 testability） | 真的需要遊戲迴圈/幀/物理的整合測試 |

**選型鐵律**：**能用 EditMode 就別用 PlayMode**——EditMode 快十倍以上，能跑幾百個。做法是把邏輯抽離成不依賴 Unity 的純 C#（見 `test-testability.md`），用 EditMode 大量快速測；PlayMode 只留給「非得有遊戲迴圈」的整合測試。

## 基本結構

```csharp
public class DamageTests
{
    [Test]                                    // EditMode：純邏輯，瞬間跑完
    public void Armor_ReducesDamage()
    {
        var result = DamageCalculator.Compute(attack: 100, armor: 30);
        Assert.AreEqual(70, result);
    }

    [UnityTest]                               // PlayMode：需要跨幀
    public IEnumerator Projectile_HitsTarget_AfterFrames()
    {
        var proj = SpawnProjectile();
        yield return new WaitForSeconds(0.5f); // 等真實時間/幀
        Assert.IsTrue(proj.HasHit);
    }
}
```

- `[Test]`：同步、瞬間——EditMode 主力。
- `[UnityTest]` + `IEnumerator`：可 `yield` 等幀/等秒——PlayMode 測跨幀行為（協程、物理沉降、非同步完成）。
- `[SetUp]`/`[TearDown]`：每個測試前後（建/清場景物件）。

## Assembly Definition：測試要隔離

- **測試放獨立的 asmdef**：測試組件引用被測組件 + `UNITY_INCLUDE_TESTS`——測試碼不進正式 build。
- **被測程式碼要可被引用**：正式碼也要有 asmdef，測試 asmdef 才能引用它——沒有 asmdef 的散裝 script 難以組織測試。
- **EditMode 測試 asmdef 標 Editor 平台**；PlayMode 的標一般平台。

## PlayMode 的特殊性（測跨幀）

- **等待要用 yield**：`yield return null`（等一幀）、`WaitForSeconds`、`WaitUntil(() => cond)`——別用 `Thread.Sleep`（凍住編輯器）。
- **非同步完成**：等 UniTask/Addressables 完成用 `yield return op.ToCoroutine()` 或轉 `WaitUntil`（見 `script-async.md`、`asset-loading.md`）。
- **場景載入**：`yield return SceneManager.LoadSceneAsync(...)` 等載完再斷言。
- **物理要跑幀**：碰撞/沉降要 `yield` 幾個 FixedUpdate 才發生——不能同步斷言。

## 常見坑

- **什麼都用 PlayMode**：測試套件慢到沒人跑——純邏輯抽離走 EditMode（見 `test-testability.md`）。
- **測試碼進 build**：沒隔離 asmdef——測試 asmdef + `UNITY_INCLUDE_TESTS`。
- **PlayMode 用 Thread.Sleep**：凍住編輯器、不跑幀——用 `yield return`。
- **同步斷言跨幀行為**：spawn 完立刻檢查命中（還沒跑幀）——`[UnityTest]` + yield 等。
- **測到引擎不是自己的邏輯**：測「Rigidbody 會不會掉」是測 Unity 物理，不是測你的 code——測你的決策邏輯，不測引擎。
