# 架構黏合：服務、通訊、組件快取

game-dev 的 system-foundation 講「模組怎麼組織、事件怎麼派發」（引擎中立）；這篇是那些決策在 Unity 的落地——服務怎麼取用、組件怎麼溝通、參照怎麼快取。

## 取用服務：三種做法的取捨

| 做法 | 是什麼 | 適合 | 痛點 |
|------|--------|------|------|
| **static singleton** | `GameManager.Instance` | 快、小專案 | 隱式依賴、難測試、初始化順序靠運氣、場景切換殘留 |
| **服務註冊表 / locator** | 中央 `Services.Get<T>()` | 中型專案，取用點集中 | 仍是全域，但依賴可搜尋、可替換 |
| **DI 容器**（Zenject / VContainer） | 建構式/欄位注入 | 大型、重測試 | 學習成本、過度使用變魔法 |

**建議**：小專案 locator 夠用（勝過散落的 `XxxManager.Instance`）；重測試或團隊協作才上 DI 容器。無論哪種，**取用點要集中**——散落全專案的 `.Instance` 是隱式依賴網（對應 game-dev 的 system-foundation 服務註冊）。

**跨場景物件走註冊，不走 Find**：主相機、玩家、音訊監聽器這種「跨場景關鍵物件」註冊到服務表，用 `Services.Get` 取——不要用 `Camera.main`、`GameObject.Find`、`FindObjectOfType`（全域搜尋、多場景撿錯、慢，見 `script-lifecycle-execution.md` 的 Camera.main 坑）。

## 組件通訊：事件 vs 直接參照

- **先問要不要事件**：A 本來就該知道 B（角色呼叫自己的血條），直接持有參照——事件不是解耦萬靈丹，濫用事件把呼叫鏈打散成沒人追得動的隱式流程（對應 game-dev system-foundation 的同一警告）。
- **事件用在「發生者不該知道誰在聽」**：擊殺事件（成就、任務、統計都在聽）。
- **Unity 的事件選項**：
  - **C# event / Action**：程式內、快、無 Inspector 曝露——邏輯層預設。
  - **UnityEvent**：可在 Inspector 拉線——設計師可配，但反射慢、難追來源，留給真的需要編輯器配置的地方。
  - **ScriptableObject 事件通道**：解耦的全域事件（見 `asset-scriptableobject.md`）——跨系統、跨場景的鬆耦合事件。
- **訂閱綁生命週期**：OnEnable 訂、OnDisable 退，成對——忘退訂是幽靈回呼與洩漏之王。

## 組件快取：GetComponent 的紀律

**`GetComponent` 是搜尋，不是欄位存取**——每次呼叫都遍歷組件。

```csharp
// 錯：Update 裡每幀 GetComponent
void Update() { GetComponent<Rigidbody>().velocity = ...; }

// 對：Awake 快取一次
Rigidbody _rb;
void Awake() { _rb = GetComponent<Rigidbody>(); }
void Update() { _rb.velocity = ...; }
```

- **一律 Awake 快取**：自身組件在 Awake 抓進 `_` 前綴欄位，之後用欄位（見 `../../unity-optimization/references/perf-gc-and-memory.md`——這也是效能項）。
- **`[RequireComponent]`** 宣告依賴，保證組件存在、省掉 null 檢查。
- **別的物件的組件**：透過服務或明確的 SerializeField 參照，不要每幀 `Find + GetComponent`。

## 資料驅動的 Unity 落地

game-dev 的 data-config-driven（數值外化成表）在 Unity 首選 **ScriptableObject**（見 `asset-scriptableobject.md`），不是散落程式碼的常數。技能/道具/敵人資料做成 SO 資產，程式讀 SO——這是 Unity 版的「內容即資料」。

## 常見坑

- **`.Instance` 滿天飛**：初始化順序靠檔名運氣、測試無法替換。取用點集中到服務表。
- **UnityEvent 當程式內事件用**：反射慢、Inspector 拉線難追、序列化脆弱。程式內用 C# event。
- **Find/FindObjectOfType 在執行期**：慢且脆（撿錯、找不到）。啟動時解析一次存起來，或走服務註冊。
- **忘記退訂**：靜態事件（尤其 SO 事件通道）持有已銷毀物件的回呼——生命週期成對訂閱/退訂。
