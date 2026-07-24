# NGO 實作模式（NetworkVariable / RPC / ownership）

選了 Netcode for GameObjects（見 `net-solution-selection.md`）之後的核心決策：狀態同步用 NetworkVariable 還是 RPC、誰有 ownership、NetworkTransform 怎麼不抖。這些模式對應 game-dev net 的引擎中立原則，這篇是 NGO 落地。（其他方案如 Mirror/FishNet 概念類似，API 不同。）

## 基本結構

- **NetworkObject**：可被網路同步的物件（要 spawn，`GetComponent<NetworkObject>().Spawn()`）——伺服器 spawn，客戶端自動生成代理。
- **NetworkBehaviour**：取代 MonoBehaviour，能用 NetworkVariable/RPC。
- **NetworkManager**：連線、spawn、host/client/server 模式的中樞。

## NetworkVariable vs RPC：狀態 vs 事件

這是 NGO 最核心的選擇，對應 game-dev net-protocol 的「Notify 是事件不是狀態、狀態以快照兜底」：

| | NetworkVariable | RPC（ServerRpc/ClientRpc） |
|--|-----------------|---------------------------|
| 本質 | **持續狀態**（值改變自動同步給所有人） | **一次性事件**（呼叫一次） |
| 用途 | 血量、位置、分數、狀態——**新加入的客戶端自動拿到當前值** | 開火、跳躍、播特效、一次性通知 |
| 漏收 | 自我修復（下次同步是最新值） | 漏收就沒了（reliable RPC 才必達） |

**準則**（同 game-dev net-protocol 的「事件加速、快照兜底」）：**持續狀態用 NetworkVariable**（漏收會自癒、晚加入者自動同步）、**一次性動作用 RPC**。血量用 NetworkVariable，不要用 RPC 廣播「血量變了」（漏一個就永久錯，game-dev net-protocol 的坑）。

```csharp
public class Player : NetworkBehaviour
{
    NetworkVariable<int> _hp = new(100, writePerm: NetworkVariableWritePermission.Server);

    [ServerRpc] void FireServerRpc() { /* 伺服器驗證後執行、可能 ClientRpc 廣播特效 */ }
    [ClientRpc] void PlayHitVfxClientRpc(Vector3 pos) { /* 所有客戶端播特效 */ }
}
```

## Ownership 與 Authority

- **伺服器權威預設**：NetworkVariable 的 write permission 預設 Server——客戶端不能直接改（game-dev net-protocol 的「客戶端不可信」）。客戶端要改狀態走 **ServerRpc**（送 intent，伺服器驗證後改，接 `../../unity-scripting/references/input-architecture.md`）。
- **Client ownership 的下放**：不影響勝負的（表情、非權威裝飾）可給 client 權限（game-dev net-server 的權威分割「不影響勝負的可下放」）——但競技核心永遠 server 權威。
- **`IsOwner` / `IsServer` / `IsClient`**：NetworkBehaviour 裡判斷角色——輸入只在 `IsOwner` 讀、權威邏輯只在 `IsServer` 跑。

## NetworkTransform：位置同步的坑

- **NetworkTransform 同步位置/旋轉**——但預設 server 權威（client 動不了自己）；要 client 控制用 **ClientNetworkTransform**（owner 權威）或走 ServerRpc + 伺服器移動。
- **抖動**：直接同步遠端位置會抖——NGO 有內建插值（interpolate），對應 game-dev net-prediction-and-latency 的延遲插值（別人的角色永遠在兩個快照間插值）。
- **本地預測**：NGO 基礎的預測有限——要真正的 client prediction + reconciliation（game-dev net-prediction）多半要自己疊或用 FishNet/Fusion（見 `net-solution-selection.md`）。

## 序列化

- **NetworkVariable 的型別**：內建型別或實作 `INetworkSerializable` 的 struct——用 struct + 純資料（game-dev data-network-sync 的純資料序列化）。
- **量化**：位置不需 full precision——量化省頻寬（game-dev net-protocol 的 quantization）。

## 常見坑

- **狀態用 RPC 廣播**：漏一個 client 永久錯——持續狀態用 NetworkVariable（自癒）。
- **client 直接改 NetworkVariable**：權限錯誤/被作弊——client 走 ServerRpc 送 intent，server 改。
- **忘了 Spawn**：NetworkObject 沒 `Spawn()` 客戶端看不到——server spawn。
- **NetworkTransform 直接同步不插值**：遠端角色抖——用插值（game-dev net-prediction）。
- **在 client 跑權威邏輯**：`IsServer` 沒判斷，每個 client 都算一遍——權威邏輯圈 IsServer。
- **以為 NGO 內建完整預測**：基礎預測有限，動作遊戲要自疊或換方案（FishNet/Fusion）。
