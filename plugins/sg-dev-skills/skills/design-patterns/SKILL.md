---
name: design-patterns
description: 設計模式的選型與坑（語言中立，不教定義）：singleton 的三宗罪與替代階梯（傳參/注入/服務定位）、狀態機 FSM 三種實作選型（enum+switch vs state 物件 vs 轉移表）、factory/strategy/observer 的進場訊號與代價。當問「要不要做成 singleton」「狀態機怎麼實作」「該不該用某個 pattern」時使用。
---

# 設計模式（Design Patterns）

> **定位**：pattern 的**選型與坑**，不教定義與 UML（已知）。與 `clean-code` 分層：那邊是微觀可讀性（命名/函式/smell），這邊是結構選型。遊戲系統的宏觀設計（模組生命週期、遊戲 AI 架構）在 **sg-game-dev-skills**，Unity 落地在 **sg-unity-dev-skills**。

貫穿鐵律：**先有痛，再上 pattern**——每個 pattern 都有「進場訊號」，訊號沒出現就別上。

| 何時 | 讀 |
|------|-----|
| 要不要 singleton／該換成什麼、狀態機三實作選型、其餘 pattern 的進場訊號與 observer 兩筆債 | `references/pattern-selection.md` |
