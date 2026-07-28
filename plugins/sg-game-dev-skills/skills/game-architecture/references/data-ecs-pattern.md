# Entity Component System（ECS）

ECS 是資料與行為分離的典型架構落地：把遊戲物件拆成 **Entity（身分）+ Component（純資料）+ System（無狀態行為）**。它天生對批次處理與組合式設計友善。

## 三個組成

- **Entity**：只是一個 id，本身不含資料，代表「一個東西」。
- **Component**：純資料片段，掛在 entity 上（Position、Velocity、Health、Sprite…）。無方法。
- **System**：無狀態邏輯，宣告「我要處理擁有某組 component 的所有 entity」，然後批次跑。

```
# Component 都是純資料
struct Position: x, y
struct Velocity: dx, dy

# System 宣告關注的 component 組合，批次處理
function MovementSystem(world, dt):
    for entity in world.query(Position, Velocity):
        pos = world.get(entity, Position)
        vel = world.get(entity, Velocity)
        pos.x += vel.dx * dt
        pos.y += vel.dy * dt
```

## 為什麼用 ECS

- **組合優於繼承**：要一個「會飛、會噴火、可被撿」的東西，就掛 Flying + FireBreath + Pickable 三個 component，不必設計一棵爆炸的繼承樹。
- **批次效能**：同型 component 連續存放（SoA 精神，見 `data-oriented-layout.md`），system 線性掃過，cache 友善。
- **清楚的資料流**：system 的執行順序即是每幀的資料處理管線，好推理、好平行化。
- **易序列化 / 同步**：世界狀態就是一堆 component 資料，天生好存檔與網路複製（見 `data-network-sync.md`）。

## 資料流（一幀）

```
輸入 → InputSystem 寫 Intent component
     → AISystem 讀感知、寫 Intent
     → MovementSystem 讀 Intent+Velocity、寫 Position
     → CollisionSystem 讀 Position、寫 Collision 事件
     → DamageSystem 讀 Collision、改 Health
     → RenderSystem 讀 Position+Sprite、畫圖
```

每個 system 只透過 component 資料溝通，不直接呼叫彼此。

## 何時用 ECS

- 大量、同型、每幀更新的實體（射擊、RTS、模擬、開放世界）。
- 物件種類靠「特性組合」爆炸成長，繼承樹難以維護。
- 需要高效批次、平行化、或狀態同步。

## 何時**不**要用 ECS

- 小型專案 / 原型：ECS 的樣板與心智負擔可能大於收益，直接物件也夠。
- 實體少、邏輯高度客製、彼此關係複雜（例如少數幾個獨特 boss 的腳本）：直接寫更直覺。
- 團隊不熟 ECS：錯用（在 component 裡塞邏輯、system 之間偷偷共享狀態）會兩頭皆失。

## 陷阱

- **component 裡放行為**：一旦 component 長出方法或自帶邏輯，就退回 OOP，失去批次與序列化的好處。component 只放資料。
- **system 藏狀態**：system 應無狀態；跨幀要記的東西也做成 component / 資源資料。
- **過度細分 component / system**：切太碎導致大量 query 與重複遍歷；以「一起被處理的資料」為分界。
- **忽略執行順序與相依**：system 順序錯了會讀到上一幀的舊資料或造成一幀延遲；明確定義管線順序。
- **query 每幀重算成本**：大世界要考慮 archetype / 快取 query 結果，別每幀線性掃全世界。
- **不必全盤 ECS**：可只在熱路徑（大量實體）用 ECS，其餘系統維持一般寫法——混合往往最務實。
