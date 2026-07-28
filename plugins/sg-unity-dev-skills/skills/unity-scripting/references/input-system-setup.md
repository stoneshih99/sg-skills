# Input System：新 vs 舊與設定

Unity 有兩套輸入系統並存——舊的 Input Manager（`Input.GetKey`）與新的 Input System package（Action-based）。選錯的代價是重綁鍵/多裝置要自己造輪子，或為簡單需求扛過重的設定。

## 新 vs 舊選型

| | 舊 Input Manager | 新 Input System（package） |
|--|------------------|---------------------------|
| 讀法 | `Input.GetKey/GetAxis`（全域輪詢） | Action-based（綁定抽象化） |
| 重綁鍵 | **自己造** | **內建**（PerformInteractiveRebinding，見 `input-architecture.md`） |
| 多裝置/控制方案 | 手動判斷 | **內建**（Control Schemes 自動切換） |
| 手把 | 靠 axis/button 編號硬對 | 裝置無關的 binding |
| 成本 | 零設定、直覺 | 需設 Action Asset、學習曲線 |

**選型**：
- **需要重綁鍵、多裝置、手把 + 鍵鼠切換**（多數正式專案）→ **新 Input System**（那些功能內建，自己造舊系統的等價物很痛，且重綁鍵是無障礙基本盤，見 game-dev ui-accessibility）。
- **game jam / 極簡原型 / 單一固定輸入** → 舊 Input Manager 的零設定夠快。
- **不要混用兩套讀同一輸入**——Project Settings 的 Active Input Handling 選一個（或 Both 但別重複讀）。

## Action-based 結構（新系統）

```
Input Action Asset（.inputactions 資產）
├── Action Map: "Gameplay"（一組情境的動作）
│   ├── Action: "Move"  (Value, Vector2)  ← binding: WASD / 左搖桿
│   ├── Action: "Jump"  (Button)          ← binding: Space / A鍵
│   └── Action: "Fire"  (Button)
├── Action Map: "UI"（選單情境）
└── Control Schemes: Keyboard&Mouse / Gamepad
```

- **Action Map 對應情境**：Gameplay / UI / Vehicle 各一個 map——切情境就切 map（`actionMap.Enable()/Disable()`），避免「選單裡按跳躍還在跳」。
- **Action 是抽象動作**：「Jump」不綁死按鍵，binding 才是具體鍵——這是重綁鍵與多裝置的基礎（見 `input-architecture.md`）。

## 三種讀取方式

| 方式 | 是什麼 | 適合 |
|------|--------|------|
| **PlayerInput component** | 掛組件、Inspector 連事件（Unity Events / Send Messages / Invoke C# Events） | 快速上手、設計師可連 |
| **手動 C# callback** | `action.performed += ctx => ...` 訂閱 | 程式控制、集中處理（推薦，見 `input-architecture.md`） |
| **Polling** | `action.ReadValue<Vector2>()` 每幀讀 | 連續值（移動軸）在 Update 讀 |

**建議**：**離散動作（跳、攻擊）用 callback**（不漏幀，見 game-dev feel-input-responsiveness 的每幀事件別在 FixedUpdate 讀）、**連續值（移動）用 polling**（Update 讀 ReadValue）——callback 集中到輸入層產 intent（見 `input-architecture.md`）。

## 生命週期坑

- **Action 要 Enable 才有效**：新 Input System 的 action 預設 disabled——忘了 `Enable()` 就是「輸入沒反應」且無報錯。用 PlayerInput 組件會自動管，手動用要自己 Enable/Disable。
- **訂閱要退訂**：`action.performed += ...` 綁在 OnEnable、`-=` 在 OnDisable（同 `script-architecture-glue.md` 的事件生命週期）——否則物件停用還在收輸入。
- **Action Map 切換時機**：進選單 Enable UI map + Disable Gameplay map，別讓兩個 map 同時吃同一鍵。

## 常見坑

- **混用新舊兩套**：Active Input Handling 沒選對、重複讀——選一套。
- **忘了 Enable action**：輸入沒反應無報錯——手動讀記得 Enable。
- **離散動作用 polling**：`ReadValue` 在 Update 讀跳躍鍵可能漏幀邊界——離散用 callback（見 feel-input-responsiveness）。
- **選單/遊戲共用一個 map**：情境沒切、按鍵串味——Action Map 分情境。
- **為極簡原型上新系統**：設 Action Asset 的成本 > 收益——jam 用舊的。
