# 輸入架構：意圖分層、重綁、容錯

輸入處理散在各處（`if (Input.GetKey)` 到處寫）是 AI 接不進來、回放做不了、重綁鍵補不上的根源。game-dev system-3c 的「輸入 → 意圖 → 執行」分層是引擎中立架構，這篇是 Unity 落地；輸入容錯（buffer/coyote）是 game-dev feel-input-responsiveness 的落地。

## 輸入 → 意圖分層（system-3c 落地）

**輸入層是唯一碰裝置的地方，產出 Intent（純資料），遊戲邏輯只讀 Intent**：

```csharp
// Intent：一份純資料快照（見 game-dev system-3c、data-separation）
public struct InputIntent { public Vector2 move; public bool jumpQueued; public bool attackQueued; }

// 輸入層：Input System callback/polling → 填 intent
public class PlayerInputReader : MonoBehaviour
{
    public InputIntent Intent;
    void OnMove(InputValue v) => Intent.move = v.Get<Vector2>();     // 連續值 polling
    void OnJump(InputValue v) { if (v.isPressed) Intent.jumpQueued = true; }  // 離散 callback
}

// Character：只讀 Intent，不碰 Input System
public class Character : MonoBehaviour
{
    void FixedUpdate() { if (_input.Intent.jumpQueued) { Jump(); _input.Intent.jumpQueued = false; } }
}
```

紅利（同 game-dev system-3c）：
- **AI 共用 Character**：AI 產同樣的 Intent，Character 完全不知道驅動者是玩家還是 AI（見 game-dev system-game-ai 執行走 intent）。
- **回放/測試**：錄 Intent 序列重播；測試餵假 Intent（見 `test-testability.md` 的可測性）。
- **重綁鍵、多裝置只影響輸入層**——Character 不動。

## 方向解算：搖桿的「前」是相機的前

- 移動 intent 的世界方向 = **相機朝向 × 搖桿輸入**（見 game-dev system-3c）——`camera.transform` 轉換搖桿的 Vector2 到世界方向。這是輸入層的責任，Character 收到的是已解算的世界方向 intent。

## 重綁鍵（Rebinding）

新 Input System 內建（舊系統要自己造，選型見 `input-system-setup.md`）——這是無障礙基本盤（game-dev ui-accessibility 的重綁鍵）：

```csharp
action.PerformInteractiveRebinding()
    .WithControlsExcluding("Mouse")
    .OnComplete(op => { SaveBindingOverride(); op.Dispose(); })
    .Start();
// 存：action.SaveBindingOverridesAsJson() → PlayerPrefs/檔案；載入時 LoadBindingOverridesFromJson
```

- **存讀 binding override**：重綁結果序列化存檔（PlayerPrefs 或存檔系統，見 game-dev system-foundation 存檔）。
- **衝突偵測**：重綁時檢查該鍵是否已綁別的 action。

## 輸入容錯（feel-input-responsiveness 落地）

game-dev feel-input-responsiveness 的容錯機制在 Unity 的落地——**緩衝的是 intent 不是按鍵**：

- **Input Buffer**：跳躍/攻擊 callback 設 `jumpQueued=true` + 時間戳，Character 在可行動幀查詢（100-200ms 內有效就執行）——不是「掐準那一幀」。
- **Coyote Time**：離開平台後短時間仍可跳——狀態記「離地時間」，跳躍 intent 在窗口內仍放行。
- **Jump Buffer**：落地前按跳，落地瞬間自動跳——queued intent 在落地幀消費。
- 這些是**遊戲邏輯層的判定**（讀 intent + 時間），不是 Input System 的事——Input System 只負責把「按了跳」變成 intent。

## 常見坑

- **`if (Input.GetKey)` 散落各處**：AI 接不進、回放做不了、重綁補不上——集中到輸入層產 intent（system-3c）。
- **Character 直接讀 Input System**：跳過 intent 層——邏輯焊死在輸入實作上。
- **重綁不存檔**：玩家改的鍵重開遊戲沒了——序列化 binding override。
- **buffer 緩衝按鍵而非意圖**：緩衝的是「意圖」（見 feel-input-responsiveness）——Character 查 intent buffer。
- **方向解算放在 Character**：Character 不該知道相機——輸入層解算後給世界方向 intent。
