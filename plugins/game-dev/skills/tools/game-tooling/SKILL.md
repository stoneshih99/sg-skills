---
name: game-tooling
description: 遊戲開發工具鏈的單一知識入口。涵蓋：除錯工具箱（debug draw 可視化、開發者控制台與作弊指令、時間控制暫停/慢動作/逐幀、日誌策略）、效能剖析與優化（先量測再優化的方法論、幀預算、profiler 判讀、常見熱點對照、批次/池化/LOD 手法選擇）、遙測與數據分析（事件埋點 schema、新手漏斗與留存、假設驅動決策）。當「這 bug 看不到發生什麼事」「測試好慢每次都要重打」「遊戲很卡」「效能不夠、先量測還先優化」「怎麼找瓶頸」「要埋哪些點」「玩家都在哪流失」「這改動有沒有效」時使用。三者對應開發期→打磨期→營運期的觀測需求。引擎中立。
---

# 遊戲工具鏈（Game Tooling）

> **定位**：本 skill 是除錯、效能、遙測三類**開發基礎設施**的知識入口，非可執行工作流。共同精神：**看得見才修得動**——開發期看內部狀態（debug）、打磨期看時間去哪了（perf）、營運期看玩家做什麼（telemetry）。

**先查域總表，再進細表。**

## 域總表

| 你的問題 | 域 | 細表 |
|----------|----|------|
| 追不到 bug、想跳到測試情境、要慢動作觀察 | 除錯工具 | ↓ Debug |
| 掉幀、卡頓、載入慢、要選優化手法 | 效能 | ↓ Perf |
| 埋點、漏斗、留存、用數據驗證改動 | 遙測 | ↓ Telemetry |

貫穿原則：**工具是正式功能**（進版控、有開關、發佈版剝離）；**先量測再下結論**（效能與數據同一條紀律）。

## Debug（除錯工具箱）

建置優先順序：draw → 作弊指令 → 時間控制 → 日誌，每層立刻回本。

| 何時 | 讀 |
|------|-----|
| 把看不見的變看得見（碰撞/路徑/視野可視化、watch 面板） | `references/debug-draw.md` |
| 控制台與作弊指令（跳關/無敵/生成、情境書籤） | `references/debug-console-and-cheats.md` |
| 時序 bug、調手感（timescale、暫停、逐幀步進） | `references/debug-time-control.md` |
| 日誌分級、頻率控制、屍檢埋點 | `references/debug-logging.md` |

## Perf（效能剖析與優化）

鐵律：先量測 → 再優化 → 量測驗證；一次只改一項。

| 何時 | 讀 |
|------|-----|
| 開始任何效能工作前（必讀）：幀預算、spike vs 均值、profiler 紀律 | `references/perf-measurement-first.md` |
| 量測後對照定位：渲染 / GC / 物理 / 邏輯 / 載入的典型肇因 | `references/perf-common-hotspots.md` |
| 已定位熱點、選手法：少做事 → 換時機 → 換結構三層 | `references/perf-optimization-playbook.md` |

## Telemetry（遙測與數據分析）

定位：遙測答「多少人、在哪」；「為什麼」交給玩測（見 `../../planning/game-design/` 的 Playtest 域）。

| 何時 | 讀 |
|------|-----|
| 規劃埋點（必讀）：事件 schema、命名、核心事件清單、隱私 | `references/telemetry-event-design.md` |
| 建核心報表：新手漏斗、D1/D7/D30、session 指標 | `references/telemetry-funnels-retention.md` |
| 拿數據下結論前：假設驅動、對照、解讀陷阱 | `references/telemetry-data-to-decision.md` |

三域相接的熱點：日誌的效能異常埋點（`debug-logging.md`）餵 perf 的量測；perf 的重負載場景同時是可讀性驗收場景；遙測事件表與日誌同一套屍檢思維。

## 相鄰 skill

- 程式架構（資料佈局 / 容器選型——perf 熱點的根本解）：`../../architecture/game-architecture/`
- 玩測（質化驗證，與遙測互補）：`../../planning/game-design/`
- 發佈與合規（發佈版剝離、隱私）：`../../workflow/game-production/`
