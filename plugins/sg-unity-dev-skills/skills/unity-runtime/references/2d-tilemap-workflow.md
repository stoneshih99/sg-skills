# Unity Tilemap 工作流：Rule Tile / 碰撞 / Runtime 操作

規範層（tileset 規格與 id 穩定、autotile 模板、層結構、內建 vs 外部編輯器選型）在 **sg-game-dev-skills** 的 art-tileset-tilemap-standards；排序（Individual vs Chunk、iso 設定）見 `2d-sorting-and-isometric.md`。這篇是 Unity 元件落地。

## 元件組合：一個 Grid、一層一個 Tilemap

```
Grid
├── ground     (Tilemap + Renderer: Chunk mode, sorting layer=Ground)
├── deco       (Chunk, Ground 之上)
├── obstacle   (Individual mode——參與 y-sort)
├── overlay    (Chunk, sorting layer=Overlay)
├── collision  (Tilemap + TilemapCollider2D，Renderer 停用)
└── logic      (Renderer 停用，只在編輯期畫 gizmo)
```

- **層 = Tilemap 子物件，名字照規範**——載入器與工具按名字找層。
- **磚縫閃線的 Unity 解法**：資產期 extrude 為主；輔以 Sprite Atlas 打包（padding ≥4）＋ Pixel Perfect Camera——只靠相機端救，換個解析度又閃。

## Rule Tile（2D Tilemap Extras package）

- **Rule Tile 就是 16/47 模板的落地**：鄰接規則設一次，鋪圖自動選磚。
- **Rule Override Tile 換皮不重寫規則**：草地規則做好，雪地/沙地用 Override 換 sprite——季節變體零規則成本。
- **Animated Tile**（水面、岩漿）與 **Prefab 掛載**（Rule Tile 的 GameObject 欄位：火把磚自帶光源與粒子）——tile 帶引擎物件是內建工作流的獨有優勢（規範篇選型表的那條）。
- **自訂 tile 屬性**：繼承 `TileBase`/`Tile` 的 ScriptableObject 可帶欄位，但**別做 50 個 SO 手填屬性**——屬性住外部表（id→屬性），SO 只留渲染設定（資料驅動，見 game-dev 規範篇）。

## 碰撞：Composite 是必配不是選配

```csharp
// collision 層的標準三件套：
// TilemapCollider2D（Used By Composite ✓）
// + CompositeCollider2D（Geometry Type: Polygons）
// + Rigidbody2D（Body Type: Static）
```

- **不合成的代價是雙殺**：每磚一個獨立 collider（效能）＋磚縫的 **ghost collision**——角色在平地行走莫名卡住/彈跳，就是踢到磚與磚之間的內部邊。Composite 把整片合成外輪廓，兩個問題同時消失。
- collision 層 Renderer 停用——視覺與碰撞分離的落地；除錯要看就開 Physics2D 的 collider gizmo。

## Runtime 操作與程序生成

- **批次寫入**：`SetTiles` / `BoxFill` / `SetTilesBlock`——程序生成逐格 `SetTile` 幾萬格，每格觸發鄰接刷新與碰撞重算，卡到懷疑人生。先組陣列一次寫。
- **讀取查表**：`GetTile` 拿到的是共用 tile 資產（改它=改全地圖同種磚）——per-cell 狀態（血量、開關）另存字典 `cell → state`，tilemap 只管外觀。
- **大改後的碰撞重算**：CompositeCollider2D 的 Generation Type 設 Manual，批次改完手動重生——Synchronous 在大量 SetTile 時反覆重算。

## 外部編輯器路線（選了 LDtk/Tiled 才讀）

- importer 是管線核心：**LDtk to Unity**、**SuperTiled2Unity**——importer 版本與編輯器版本一起鎖進專案文件（與 Spine runtime 配對同一條紀律）。
- 外部的 logic 層（entity、觸發區）進 Unity 後轉成什麼（prefab 實例化/ScriptableObject 資料）在 importer 設定裡定一次——別每關手工補。

## 常見坑

- **沒掛 Composite**：ghost collision 平地卡角＋collider 數量爆炸。
- **逐格 SetTile 程序生成**：批次 API。
- **改 GetTile 回來的 tile**：全地圖同種磚一起變——per-cell 狀態另存。
- **磚縫閃線**：資產 extrude + Atlas padding，別只調相機。
- **50 個 tile SO 手填屬性**：屬性進外部表。
- **importer 版本不鎖**：編輯器升級，全部關卡重匯出。
