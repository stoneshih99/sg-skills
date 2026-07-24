# Rigidbody 與碰撞

Unity 物理（PhysX）的「方便寫法」有很多隱藏坑：抖動、穿牆、碰撞不觸發。這篇是 Rigidbody 與碰撞的決策與坑。game-dev algo-physics 的向量/碰撞**數學**是引擎中立，這篇是 Unity 引擎的落地；角色控制的 kinematic vs 物理驅動決策見 game-dev system-3c。

## Rigidbody：三種身份

| 身份 | 設定 | 誰移動它 | 適合 |
|------|------|---------|------|
| **動態 Rigidbody** | 有 Rigidbody、非 kinematic | 物理引擎（施力/重力） | 被物理推的東西（掉落物、載具、擊飛） |
| **Kinematic Rigidbody** | 有 Rigidbody、`isKinematic=true` | 你的程式（改 transform/MovePosition） | 程式控制但要參與碰撞的（平台、程式驅動角色，見 system-3c 的 kinematic controller） |
| **靜態碰撞體** | 只有 Collider、**無 Rigidbody** | 不動 | 場景牆壁地板 |

**鐵律：要移動的東西不要只有 Collider（無 Rigidbody）**——移動「靜態碰撞體」會讓 PhysX 每次重建靜態碰撞資料，效能災難且碰撞偵測不可靠。會動就給 Rigidbody（動態或 kinematic）。

## 施力在 FixedUpdate

- **物理操作（AddForce、velocity、MovePosition）在 `FixedUpdate`**，不是 Update（見 `../../unity-scripting/references/script-lifecycle-execution.md`）——Update 施力會隨 framerate 不一致。
- **移動 kinematic Rigidbody 用 `MovePosition`/`MoveRotation`**，不直接改 `transform.position`——MovePosition 會做插值與正確的碰撞掃掠；直接設 transform 會瞬移穿過碰撞。

## Interpolation：消除物理抖動

物理跑固定步長（FixedUpdate），渲染跑可變幀率——不處理就是規律抖動：

- **Rigidbody 的 Interpolate 設 Interpolate**：讓渲染在物理步之間插值，視覺平滑（對應 game-dev system-3c 的物理插值、渲染跟插值位置）。
- 只對「玩家看的、會動的」開（相機跟隨的角色）——全開有成本。

## CCD：防穿隧（高速物體）

**快速移動的小物體會穿過薄牆**——單步位移大於障礙厚度，離散碰撞漏判（game-dev algo-physics 的穿隧問題）：

- **Collision Detection 設 Continuous**（或 Continuous Dynamic）：對高速物體開 CCD——子彈、快速投射物。
- 或用 raycast/掃掠自己做（見 `physics-queries-and-performance.md`、game-dev algo-physics 的高速物體 raycast）——大量子彈用 raycast 比開 CCD 便宜。
- CCD 有成本，只給真的會穿隧的物體開。

## 碰撞 vs 觸發

| | Collision（OnCollisionEnter） | Trigger（OnTriggerEnter） |
|--|------------------------------|--------------------------|
| 物理反應 | 有（會被彈開） | 無（穿過去） |
| 用途 | 實體碰撞（撞牆、堆疊） | 範圍偵測（進入區域、拾取、傷害盒） |
| Collider 設定 | 一般 | `isTrigger=true` |

**碰撞/觸發回呼觸發的前提**：**至少一方要有 Rigidbody**——兩個都是靜態碰撞體，回呼不會觸發（常見「OnTrigger 沒反應」的坑）。傷害盒/拾取盒（game-dev system-action-combat 的 hitbox/互動盒）用 Trigger + 一方帶 Rigidbody。

## 層碰撞矩陣：過濾

- **Layer Collision Matrix**（Project Settings → Physics）：定義哪些層互相碰撞——子彈不撞子彈、玩家不撞玩家的隊友（對應 game-dev system-action-combat 的碰撞層過濾）。
- **在矩陣過濾比在回呼裡 if 便宜**：關掉的層對根本不進碰撞計算——效能第一道剪枝（見 `physics-queries-and-performance.md`）。

## 常見坑

- **移動只有 Collider 的物件**：PhysX 重建靜態資料、碰撞不可靠——會動就給 Rigidbody。
- **Update 裡施力 / 直接設 transform 移動 Rigidbody**：framerate 相依、瞬移穿牆——FixedUpdate + MovePosition。
- **OnTrigger 沒反應**：兩邊都無 Rigidbody——至少一方要有。
- **高速物體穿牆**：離散碰撞漏判——CCD 或 raycast。
- **不開 interpolation 抖動**：物理步 vs 渲染幀——Interpolate。
- **在回呼裡 if 過濾碰撞**：該用層矩陣——關掉的層根本不算。
