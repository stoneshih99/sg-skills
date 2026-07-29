---
name: ship-small-game
description: Use when 使用者要把小型遊戲從構想或未完成專案一路做到可交付 Build，包含完整遊戲、垂直切片後擴充、跨企畫美術程式測試協調、接手半成品或判定是否能發佈
---

# Ship Small Game

## 定位

這是小型完整遊戲的總控 workflow。負責階段、範圍、交接、核准與證據；專業決策交給既有 hubs，不重寫其內容。

## 開始前

先讀 repository 指令與既有文件，盤點引擎、平台、工具、資產授權、測試及 Build 能力。既有證據優先；不要從對話假設專案狀態。

在取得 repository 證據前，使用者對完成度的敘述不可將階段推進到 Preflight 之後；以 Preflight、Blocked 或 Unverified 記錄，並要求最小解阻資訊。

## 決策權

- 可逆且低成本的決定可自主執行並記錄。
- 核心玩法、範圍、技術選型、授權、破壞性遷移、平台與正式發佈是重大決策，必須核准。

## 階段

Preflight → Game Contract → Production Blueprint → Vertical Slice → Content Complete → Quality Complete → Release Candidate

重大決策核准後，仍須依序完成 Game Contract 與 Production Blueprint 的證據，才能開始 Vertical Slice；不可跳過中間階段。

逐階段規則讀 [stage-gates.md](references/stage-gates.md)。

## 核心交付物

複製並依專案慣例保存四份模板：

- [game-brief.md](templates/game-brief.md)
- [delivery-roadmap.md](templates/delivery-roadmap.md)
- [acceptance-matrix.md](templates/acceptance-matrix.md)
- [production-status.md](templates/production-status.md)

## 證據邊界

每項驗收只可標記 Verified、Unverified 或 Blocked。沒有執行證據不得宣告完成。

## 路由與恢復

- 分派專業工作前讀 [department-routing.md](references/department-routing.md)。
- 接手既有專案、範圍失控或能力受阻時讀 [recovery-and-scope-control.md](references/recovery-and-scope-control.md)。
- 每次工作完成後回寫 roadmap、acceptance matrix 與 production status。
