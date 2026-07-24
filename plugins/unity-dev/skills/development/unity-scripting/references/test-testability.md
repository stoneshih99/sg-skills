# 可測性設計：把邏輯從 Unity 抽出來

Unity code 難測的根源：邏輯跟 MonoBehaviour、GetComponent、static singleton 綁死，測一個公式要先進 Play Mode 建整個場景。解法不是「更會測」，是**把邏輯設計成不依賴 Unity**——這樣 EditMode 就能瞬間大量測（見 `test-framework.md`）。可測性源於架構，這是 game-dev 的 data-separation / system-ui 在 Unity 的落地。

## 核心：純邏輯與 Unity 分離

**把「決策/計算」抽成不依賴 UnityEngine 的純 C# class，MonoBehaviour 只當薄殼**：

```csharp
// 純邏輯：plain C#，零 Unity 依賴 → EditMode 瞬間測（見 test-framework）
public static class DamageCalculator
{
    public static int Compute(int attack, int armor, bool crit)
        => Mathf_Max(1, (attack - armor)) * (crit ? 2 : 1);   // 連 Mathf 都可自寫避免依賴
}

// MonoBehaviour 薄殼：只做 Unity 的事（拿輸入、呼叫純邏輯、套用結果）
public class Combatant : MonoBehaviour
{
    public void TakeHit(int atk, bool crit)
    {
        int dmg = DamageCalculator.Compute(atk, _armor, crit);   // 邏輯在可測的地方
        _hp -= dmg;                                              // Unity 的部分留殼裡
    }
}
```

- **測 `DamageCalculator` 不需要場景、不需要 Play Mode**——純函數，餵輸入驗輸出（對應 game-dev data-separation 的「純資料 + 無狀態行為」、system-action-combat 傷害管線 1-5 階段是純計算）。
- MonoBehaviour 薄到「幾乎沒邏輯可測」——它只是接線。

## 依賴注入：mock 掉 Unity 依賴

需要 Unity 服務（時間、隨機、輸入）的邏輯，**透過介面注入**而非直接呼叫 static——測試時給假的：

```csharp
public interface IClock { float DeltaTime { get; } }
public class UnityClock : IClock { public float DeltaTime => Time.deltaTime; }

public class Cooldown
{
    readonly IClock _clock;
    public Cooldown(IClock clock) => _clock = clock;   // 注入
    // 測試時傳 FakeClock（可控時間），EditMode 驗冷卻邏輯，不靠真實時間
}
```

- **不直接碰 `Time`、`Random`、`Input`、singleton**：這些讓邏輯不可測（無法控制、無法重現）——包成介面注入（服務定位/DI 見 `script-architecture-glue.md`）。
- **可控的隨機/時間**：注入假時鐘/假亂數 → 測試可重現、可測邊界（對應 game-dev net 的決定論、data-separation）。

## 為什麼這也是好架構（不只為了測）

**可測性與好架構是同一件事**——能測代表低耦合、依賴明確、純邏輯可獨立推理。game-dev system-ui 的兩個思想實驗直接適用：

1. **砍掉 UI/場景，邏輯還能跑嗎？** 能 = 邏輯沒綁死在 MonoBehaviour → 可 EditMode 測。
2. **邏輯能不進 Play Mode 驗證嗎？** 能 = 它是純的。

所以「為了可測而抽離」順便換來低耦合、可重用、可 headless 模擬（見 game-dev system-narrative 任務可 headless 測、gdd-numeric 的自動戰鬥模擬）。

## 實務準則

- **新邏輯預設寫成純 C#**，需要時才用 MonoBehaviour 殼包起來——不是反過來（先 MonoBehaviour 再想怎麼測）。
- **MonoBehaviour 裡不寫算式**：看到 MonoBehaviour 有複雜計算/規則，抽出去。
- **ScriptableObject 資料 + 純邏輯**：資料在 SO（見 `asset-scriptableobject.md`）、邏輯在純 class、MonoBehaviour 接線——三者都可獨立測。

## 常見坑

- **邏輯焊在 MonoBehaviour**：測一個公式要建整個場景進 Play Mode——抽成純 class。
- **直接呼叫 static（Time/Random/Input/Instance）**：不可控、不可重現——介面注入。
- **測試依賴真實時間**：`WaitForSeconds` 測冷卻慢又脆——注入假時鐘，EditMode 瞬間測。
- **為了測寫一堆 mock Unity 元件**：與其 mock MonoBehaviour，不如一開始就把邏輯抽出來（不需要 mock）。
- **把可測性當測試的事**：它是架構的事——設計時就分離，不是事後補測。
