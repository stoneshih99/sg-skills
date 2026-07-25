---
name: game-architecture
description: 遊戲程式架構的單一知識入口，四域：演算法與資料結構（求解策略、pathfinding/A*、碰撞與 raycast、容器選型）、資料驅動（範式選型 OOP vs 資料驅動、資料與行為分離、cache 佈局、ECS、config 數值外化、序列化）、系統架構（戰鬥命中與傷害管線、技能/Buff/屬性、3C 角色控制與相機、敵人 AI 與行為樹、UI 架構與 MVVM、基礎設施與存檔、場景與串流、敘事對話與任務）、多人連線（lockstep/rollback/狀態同步選型、協定與斷線重連、客戶端預測與延遲補償、房間伺服器）。當要挑演算法或容器、設計上述任一系統，或問「效能太差要換什麼結構」「大量物件怎麼跑得快」「ECS 適不適合」「數值要不要做成表」「狀態怎麼同步」時使用。內容以偽代碼呈現，語言與引擎中立。
---

# 遊戲架構（Game Architecture）

> **定位**：本 skill 是遊戲程式架構的**領域知識入口**，非可執行工作流。與 plan mode 或 spec 類流程搭配時，作為架構決策的知識來源。

四個域：**演算法與資料結構**（挑對演算法和容器）、**資料驅動設計**（資料與行為的關係）、**遊戲系統架構**（具體系統的實作級設計）、**多人連線**（同步模型到伺服器）。**先查域總表，再進細表。**

## 域總表

| 你的問題 | 域 | 細表 |
|----------|----|------|
| 用什麼演算法思路、pathfinding、碰撞計算、選容器、2D/iso 視角與格子 | 演算法 | ↓ Algo |
| 資料跟邏輯怎麼切、批次效能、ECS、設定表、同步 | 資料驅動 | ↓ Data |
| 設計某個具體系統：戰鬥、技能/Buff、3C、AI、UI、基礎設施、場景、敘事 | 系統架構 | ↓ System |
| 做多人：同步模型、協定、預測、伺服器 | 多人連線 | ↓ Net |

貫穿原則：**每幀執行的東西，複雜度與配置要保守**；**保持資料純粹**（能不含行為、能批次處理、能直接序列化）。

## Algo（演算法與資料結構）

| 何時 | 讀 |
|------|-----|
| 不確定用哪種演算法「思路」（暴力/貪婪/分治/DP/回溯/雙指針） | `references/algo-problem-solving.md` |
| 2D 視角與格子：top-down/iso/2.5D 選型、座標轉換、y-sort 深度排序 | `references/algo-2d-projection-and-grids.md` |
| pathfinding、AI 搜尋、圖上搜尋（BFS/DFS/Dijkstra/A*/JPS/二分搜） | `references/algo-search.md` |
| 移動、碰撞、瞄準、平滑過渡（向量/AABB/SAT/raycast/lerp/彈道/steering） | `references/algo-physics.md` |
| 選容器、懷疑結構選錯導致效能問題（hash/heap/grid/quadtree/graph） | `references/algo-data-structures.md` |

## Data（資料驅動設計）

| 何時 | 讀 |
|------|-----|
| 不確定該用領域模型還是資料驅動（跨範式裁決表、混用策略） | `references/data-paradigm-selection.md` |
| 決定資料與邏輯怎麼切（POD vs 系統、與 OOP 對比） | `references/data-separation.md` |
| 大量物件效能吃緊（AoS/SoA、cache、批次、冷熱切分） | `references/data-oriented-layout.md` |
| 考慮 ECS 架構（何時用 / 何時不用） | `references/data-ecs-pattern.md` |
| 數值外化成設定表 / 資產（schema、載入驗證、熱重載、可 mod） | `references/data-config-driven.md` |
| 存檔 / 網路同步（序列化、快照 delta、決定論、預測校正） | `references/data-network-sync.md` |

## System（遊戲系統架構）

實作決策級：講「A 模式 vs B 模式、為什麼、何時選哪個」，非原則概述。八篇，既定候選全數完成；後續按實戰需求擴充。

| 何時 | 讀 |
|------|-----|
| 動作戰鬥：能力鎖、hitbox 兩種模式、攻擊時間軸、階段化傷害管線 | `references/system-action-combat.md` |
| 技能系統：屬性修飾器堆疊、技能資料化與階段機、buff 疊加策略 | `references/system-skill.md` |
| 3C：輸入意圖分層、kinematic vs 物理驅動、相機解算管線、更新順序 | `references/system-3c.md` |
| 遊戲 AI：FSM/BT/Utility 選型、感知刺激、攻擊 token、表演性 | `references/system-game-ai.md` |
| UI 架構：畫面堆疊管理、MVC/MVP/MVVM 選型、單向資料流與指令回流 | `references/system-ui.md` |
| 基礎設施：模組生命週期、事件派發時機、時間服務、資源 handle、存檔 | `references/system-foundation.md` |
| 場景管理：切換管線、additive 組合、串流三環、spawn 紀律 | `references/system-scene.md` |
| 敘事系統：flag store、對話節點圖與演出分離、任務狀態機、分支收斂 | `references/system-narrative.md` |

## Net（多人連線）

實作決策級。入門與序列化基礎先讀 `references/data-network-sync.md`（Data 域），以下四篇是深化。

| 何時 | 讀 |
|------|-----|
| 第一個決策：權威放哪、同步什麼（lockstep/rollback/狀態同步選型） | `references/net-model-selection.md` |
| 訊息與通道設計、序列化量化、斷線重連、安全基線 | `references/net-protocol-and-connection.md` |
| 連線手感：本地預測與和解、插值、延遲補償回捲判定 | `references/net-prediction-and-latency.md` |
| 伺服器側：tick 迴圈、房間制、持久化、AOI、部署量級 | `references/net-server-architecture.md` |

域相接的熱點：空間分割（`algo-data-structures.md`）是碰撞寬階段與範圍查詢的核心；ECS 的 component 儲存就是 SoA（`data-oriented-layout.md`）；3C 的 intent 分層是預測與 AI 的共同地基（`system-3c.md` → `net-prediction-and-latency.md`）。

## 相鄰 skill

- 效能實測與優化手法（先量測再優化）：`../../tools/game-tooling/`
- 系統關係圖 / 狀態機圖：`../../diagram/game-diagrams/`
- 生產面的資產與 config 規格：`../../workflow/game-production/`
