---
name: game-design
description: 遊戲企畫與設計的單一知識入口，四域：立項與企畫書（想點子與篩選、玩法機制、數值框架 TTK/成長曲線、核心循環、範圍、風險、目標玩家定位、經濟）、關卡設計（節奏、無文字教學、遭遇）、遊戲手感（打擊回饋、輸入容錯、移動與攝影機）、玩測（假設與判準、主持紀律、問卷訪談）。當要立新遊戲項目、寫企畫書/GDD、設計關卡、驗證原型或排玩測，或說「打擊感很虛」「操作遲鈍」「移動很飄」「這遊戲給誰玩」「數值怎麼規劃」「玩家卡在哪」時使用。引擎中立。
---

# 遊戲設計（Game Design）

> **定位**：本 skill 是遊戲企畫與設計的**領域知識入口**，非可執行工作流。涵蓋從點子到驗證的設計面：企畫書 → 關卡 → 手感 → 玩測。

**先查域總表，再進該域細表挑要讀的 reference。**

## 域總表

| 你的問題 | 域 | 細表 |
|----------|----|------|
| 立項（創意/玩法/數值）、核心循環、範圍、風險、定位、經濟 | 企畫書 | ↓ GDD |
| 設計一個關卡、節奏平淡、教學關 | 關卡 | ↓ Level |
| 「不夠爽」「遲鈍」「飄」——手感排查 | 手感 | ↓ Feel |
| 驗證原型、排玩測、問卷訪談 | 玩測 | ↓ Playtest |

貫穿原則：**行為 > 意見**（玩家做什麼比說什麼可信）、**判準先寫死**（驗證前先定成功長什麼樣）、**一次驗一個假設**。

## GDD（企畫書）

流程：問關鍵問題（一次一題）→ 套 `templates/gdd-one-pager.md` → 需要深化時讀對應篇。

| 何時 | 讀 |
|------|-----|
| 還沒有點子 / 要立項：創意生成、篩選漏斗、立項判準 | `references/gdd-ideation.md` |
| 設計玩法機制：有趣決策、深度 vs 複雜度、機制組合 | `references/gdd-mechanics-design.md` |
| 核心玩法 / 循環要拆解 | `references/gdd-core-loop-design.md` |
| 填「範圍」欄、範圍膨脹 | `references/gdd-scope-cutting.md` |
| 填「最大風險」欄、規劃原型驗證 | `references/gdd-risk-assessment.md` |
| 填「目標玩家」「一句話」、定位模糊 | `references/gdd-positioning.md` |
| 成長曲線、資源 source/sink、通膨 | `references/gdd-progression-economy.md` |
| 數值設計：錨點推導、TTK/EHP、cost curve、試算表工作流 | `references/gdd-numeric-design.md` |

## Level（關卡設計）

流程：先定這關的職責（一關一職責）→ 套 `templates/level-one-pager.md` → 深化讀對應篇。

| 何時 | 讀 |
|------|-----|
| 排整關結構、關卡「感覺平」 | `references/level-pacing-curve.md` |
| 教學關、引入新機制（四段教學法） | `references/level-teaching-through-design.md` |
| 編排單一戰鬥 / 解謎遭遇 | `references/level-encounter-design.md` |

## Feel（遊戲手感）

先定位問題類型，一次只調一項，改完試玩再調下一項。前提：核心循環已驗證好玩（打磨期才進場）。

| 症狀 | 讀 |
|------|-----|
| 「打到東西沒感覺」 | `references/feel-impact-feedback.md` |
| 「按了沒反應 / 吃指令」 | `references/feel-input-responsiveness.md` |
| 「移動飄 / 笨重」 | `references/feel-movement.md` |

## Playtest（玩測）

流程：寫假設與判準（先寫死）→ 套 `templates/playtest-plan.md` → 跑測試 → 對照判準下結論。

| 何時 | 讀 |
|------|-----|
| 規劃測試前（必讀）：假設寫法、判準、各階段測什麼 | `references/playtest-hypothesis-and-metrics.md` |
| 實際跑一場：招募、主持紀律、觀察表 | `references/playtest-running-a-session.md` |
| 設計問卷 / 訪談（不問「好不好玩」） | `references/playtest-asking-questions.md` |

## 相鄰 skill

- 生產流程與資產標準（里程碑 / 建置 / 量產 / 美術 / 音訊 / 本地化 / UI）：`../../workflow/game-production/`
- 量化驗證（遙測、漏斗、留存）：`../../tools/game-tooling/`
- 畫圖（核心循環圖 / 經濟流圖 / 畫面流程圖）：`../../diagram/game-diagrams/`
