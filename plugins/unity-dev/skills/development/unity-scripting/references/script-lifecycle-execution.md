# 生命週期與執行順序

Unity 的 MonoBehaviour 回呼順序是一切 bug 的隱形舞台——「Start 裡拿到 null」「有時對有時錯」多半是取用時機或執行順序問題。這篇是取用時機的決策表與幾個必知的坑。

## 回呼取用時機（決策表）

| 回呼 | 何時跑 | 放什麼 | 不要放什麼 |
|------|--------|--------|-----------|
| `Awake` | 物件實例化時，早於任何 Start | **快取自身參照**（GetComponent）、初始化自己的狀態 | 取用**別的**物件（對方可能還沒 Awake） |
| `OnEnable` | 每次啟用 | 訂閱事件、註冊 | 依賴別人已初始化 |
| `Start` | 第一次 Update 前，晚於全部 Awake | **取用別的物件**（此時全場 Awake 完成）、需要別人就緒的初始化 | 每幀邏輯 |
| `Update` | 每幀 | 一般遊戲邏輯、輸入讀取 | 物理施力、每幀配置（見 `../../unity-optimization/references/perf-gc-and-memory.md`） |
| `FixedUpdate` | 固定步長 | **Rigidbody 施力**、物理相關 | 讀輸入（會漏幀）、非物理邏輯 |
| `LateUpdate` | 所有 Update 後 | **相機跟隨**、依賴角色最終位置的東西 | 一般邏輯 |

**鐵律**：`Awake` 設定自己、`Start` 取用別人——跨物件參照放 Start，因為「全部 Awake 完 → 才第一個 Start」。在 Awake 裡抓別的物件是「有時 null」的頭號來源。

## Update vs FixedUpdate 的時間

- `Update` 的 `Time.deltaTime` 是變動的（跟 framerate）；`FixedUpdate` 的是固定的（`Time.fixedDeltaTime`）。
- **輸入在 Update 讀**（`GetKeyDown` 之類每幀事件在 FixedUpdate 會漏），**物理在 FixedUpdate 做**。要「Update 讀輸入 → FixedUpdate 用」時，用旗標暫存跨過去。
- 高刷新率螢幕：邏輯若綁 Update 幀率，行為會隨機器變——關鍵邏輯用固定步長或明確乘 deltaTime（對應 game-dev 的邏輯/渲染分離）。

## 執行順序（Script Execution Order）

- **預設無保證**：兩個 MonoBehaviour 的 Update 誰先跑，Unity 不保證——依賴「A 的 Update 先於 B」的隱性假設是計時炸彈。
- **顯式控制**：Project Settings → Script Execution Order 明確排（管理器類早跑、表現類晚跑）——但用得越多代表耦合越深，優先改成「不依賴順序」（事件驅動、或在 LateUpdate 收尾）。
- 更穩的做法：關鍵初始化與更新走**自己的管理器統一驅動**（見 `script-architecture-glue.md` 的服務與 game-dev 的 system-foundation 模組生命週期），而不是散在各 MonoBehaviour 靠 Unity 排序。

## 坑：`Camera.main` 是全域 tag 搜尋

`Camera.main` 每次呼叫都做一次 `FindGameObjectsWithTag("MainCamera")`——兩個成本：

1. **效能**：每幀呼叫是隱藏的全場搜尋，快取到欄位（Awake 抓一次）。
2. **正確性（更陰險）**：多場景共存時（additive 載入），若殘留的舊 Main Camera 仍掛著 `MainCamera` tag，`Camera.main` 可能撿到**錯的相機**——`ScreenToWorldPoint`、射線等座標計算全部飄掉，且**無任何錯誤訊息**。
   - **解法**：不再使用的相機拿掉 tag；跨場景關鍵物件（主相機、玩家）走服務註冊而非全域 tag/Find 查詢（見 `script-architecture-glue.md`，對應 game-dev 的 system-scene 全域查詢殘留陷阱）。

## 其他常見坑

- **在 Awake 訂閱、忘了在 OnDisable 退訂**：物件停用/銷毀後事件還在打，NullReference 或幽靈行為。訂閱綁 OnEnable、退訂綁 OnDisable，成對。
- **Destroy 不是立即**：`Destroy(obj)` 當幀結束才真的銷毀，同幀後續還讀得到——需要立即用 `DestroyImmediate`（僅編輯器）或改邏輯。
- **`OnDestroy` 在未啟用物件不保證**：從沒 Awake 過的物件不會收到 OnDestroy——清理邏輯別只依賴它。
- **協程綁在 MonoBehaviour 上**：宿主停用/銷毀協程就停（見 `script-async.md`）。
