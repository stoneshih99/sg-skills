# FishNet 實作與 EOS P2P

方案選型（NGO vs FishNet vs Mirror vs Photon 該用哪個）見 `net-solution-selection.md`；權威模型與預測的概念見 **sg-game-dev-skills** 的 net 家族。這篇是選定 FishNet 後的實作決策與坑，加上用 **Epic Online Services（EOS）做免伺服器連線**的架構真相。

## FishNet 的 API 心智（v4，從 NGO/Mirror 搬過來最容易寫錯的地方）

- **SyncVar 是泛型欄位，不是 attribute**（`[SyncVar]` 舊語法 v4 已移除）：

```csharp
private readonly SyncVar<float> _health = new(new SyncTypeSettings(1f)); // 1f = 送頻率
private void Awake() => _health.OnChange += OnHealth;   // spawn 前訂閱，Awake 是正確時機
private void OnHealth(float prev, float next, bool asServer) { /* UI 更新走這裡 */ }
// 寫入只在 server：_health.Value = next;
```

- **SyncType 家族選型**：`SyncVar<T>`（單值）/ `SyncList`/`SyncDictionary`（集合，**別整個 new，用操作方法改**）/ `SyncTimer`（倒數同步不逐幀送）。`SyncTypeSettings` 管送頻率與 `WritePermission`/`ReadPermission`（如 `ExcludeOwner`——別人看得到你看不到的機制直接用權限做）。
- **RPC 三種**：`[ServerRpc]`（owner→server，`RequireOwnership = false` 才准非 owner 呼）、`[ObserversRpc]`（server→所有觀察者）、`[TargetRpc]`（server→指定連線）；**每個 RPC 可逐呼叫選 Channel**（reliable/unreliable）——高頻位置類走 unreliable，事件類 reliable。
- **狀態用 SyncVar、事件用 RPC**：中途加入的玩家收得到 SyncVar 現值、收不到歷史 RPC——這條跟 NGO 篇（`net-ngo-patterns.md`）同一鐵律。

## Prediction v2（選 FishNet 的最大理由）

**先問要不要**：非玩家控制、或能接受輸入延遲的物件，`NetworkTransform` 平滑同步就夠——**預測是為「玩家親手控制且要零輸入延遲＋伺服器權威」的物件準備的**（概念見 game-dev 的 net-prediction-and-latency）。

```csharp
public struct MoveData : IReplicateData { public float H, V; /* + tick 樣板 */ }
public struct RecData : IReconcileData { public PredictionRigidbody Rb; /* + tick 樣板 */ }

// Update 收輸入 → OnTick 消費：
void TimeManager_OnTick() => RunInputs(BuildData());     // 非 owner 時回傳 default
[Replicate] void RunInputs(MoveData d, ReplicateState s = ReplicateState.Invalid, Channel c = Channel.Unreliable) { /* 施力 */ }
void TimeManager_OnPostTick() => CreateReconcile();
[Reconcile] void Reconcile(RecData d, Channel c = Channel.Unreliable) { /* 套回狀態 */ }
```

- **物理走 `PredictionRigidbody`**，不是直接對 Rigidbody `AddForce`——預測回滾要重放力，直接施力回滾不了。
- **輸入在 Update 收集、OnTick 消費**：在 OnTick 裡讀 `GetKeyDown` 會漏鍵（tick 頻率低於幀率）。
- **命中回捲（lag compensation）是 Pro 功能**（RollbackManager）——免費版要自己寫回捲判定，競技射擊選型時把這筆帳算進去。

## Transport 與 EOS P2P：免伺服器連線的架構真相

**先戳破名詞**：FishNet 沒有「無主機 P2P」——所謂 P2P 是 **listen server 拓撲**（一個玩家當 host 兼 server）＋ **EOS 免費中繼**解決「別人怎麼連進他家 NAT」。權威還是在 host 身上。

| Transport | 用途 |
|-----------|------|
| **Tugboat**（預設，UDP） | dedicated server、區網、有公網 IP |
| **FishyEOS** | EOS P2P relay/NAT punch——免伺服器、免固定 IP、**免費** |
| **FishySteamworks** | Steam relay（走 Steam 好友邀請生態） |
| **Bayou** | WebSocket——WebGL 版唯一的路 |
| **Multipass** | 多 transport 並存——Steam 版走 Steamworks、其他平台走 EOS，同一份遊戲碼 |

- **EOS 是 Epic 的免費後端服務，不綁 Epic 商店**：Auth（Device ID 匿名登入起步）、Lobby/匹配、P2P relay、語音——一人工作室做小隊 co-op 的零成本組合。
- **選型裁決**：競技/防作弊/長 session 穩定 → dedicated（Tugboat + 租伺服器）；**朋友開房 co-op、host 優勢可接受 → EOS P2P listen server**（權威概念的取捨見 game-dev 的 net-model-selection）。
- **EOS P2P 的三筆隱形帳**：**host 斷線＝房間死**（FishNet 沒有 host migration——流程設計成「回大廳重連」，別承諾無縫）；host 零延遲的公平性問題；relay 繞路的延遲上限。
- FishNet 的**場景管理自成體系**（global/connection scenes、scene stacking）——連線場景用它的 SceneManager 載，直接用 Unity SceneManager 載出來的場景不在同步範圍。

## 常見坑

- **`[SyncVar]` attribute 寫法**：v4 沒這東西——泛型欄位 + `.Value`。
- **OnChange 訂閱太晚**：spawn 後才訂閱漏掉初始同步——Awake 訂。
- **每個東西都上 prediction**：成本高（每 tick 重放）——只給玩家親控物件。
- **OnTick 裡讀 GetKeyDown**：漏輸入——Update 收、tick 消費。
- **拿 Unity SceneManager 載連線場景**：物件不同步——走 FishNet SceneManager。
- **把 EOS P2P 當無主機**：host 掉線全房斷——大廳重連流程第一天設計。
