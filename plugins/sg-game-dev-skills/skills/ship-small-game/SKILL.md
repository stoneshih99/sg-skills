---
name: ship-small-game
description: Use when 使用者要把小型遊戲從構想或未完成專案一路做到可交付 Build，包含完整遊戲、垂直切片後擴充、跨企畫美術程式測試協調、接手半成品或判定是否能發佈
---

# Ship Small Game

## 定位

這是小型完整遊戲的總控 workflow。負責階段、範圍、交接、核准與證據；專業決策交給既有 hubs，不重寫其內容。

## 開始前

先讀 repository 指令與既有文件，盤點引擎、平台、工具、資產授權、測試及 Build 能力。既有證據優先；不要從對話假設專案狀態。

## 決策權

- 可逆且低成本的決定可自主執行並記錄。
- 核心玩法、範圍、技術選型、授權、破壞性遷移、平台與正式發佈是重大決策，必須核准。

## 階段

Preflight → Game Contract → Production Blueprint → Vertical Slice → Content Complete → Quality Complete → Release Candidate

逐階段規則讀 [stage-gates.md](references/stage-gates.md)。

## 核心交付物

複製並依專案慣例保存四份模板：

- [game-brief.md](templates/game-brief.md)
- [delivery-roadmap.md](templates/delivery-roadmap.md)
- [acceptance-matrix.md](templates/acceptance-matrix.md)
- [production-status.md](templates/production-status.md)

## 證據邊界

每項驗收只可標記 Verified、Unverified 或 Blocked。沒有執行證據不得宣告完成。
