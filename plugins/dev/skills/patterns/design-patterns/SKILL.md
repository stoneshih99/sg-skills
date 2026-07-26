---
name: design-patterns
description: 通用設計模式的選型與坑（語言中立，不教定義）——三家族：建立型（直接 new vs factory vs builder 的進場階梯、singleton 的毒與替代階梯）、結構型（adapter/facade/bridge 意圖裁決、decorator vs 繼承、composite）、行為型（strategy vs if-else 何時值得、FSM 三種實作選型、observer 訂閱洩漏與派發時機、command 何時該包）。當「該不該用某個 pattern」「if-else/switch 重複想重構」「要不要 singleton」「adapter 跟 bridge 差在哪」「狀態機怎麼實作」時使用。收選型判準與坑，不是 pattern 教學。
---

# 設計模式（Design Patterns）

> **定位**：通用 pattern 的**選型與坑**——「這個情境該不該上、上哪個、代價是什麼」。不教定義與 UML（Claude 已知）。與 `clean-code` 分層：那邊是微觀可讀性（命名/函式/smell），這邊是結構選型。遊戲系統的宏觀設計（模組生命週期、遊戲 AI、事件通道深化）在 **sg-game-dev-skills**，Unity 落地在 **sg-unity-dev-skills**——overlap 詞（FSM/singleton/observer）的分工見各篇內文指引。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 怎麼建物件：new/factory/builder、要不要 singleton | 建立型 | ↓ Creational |
| 怎麼組結構：wrapper 該叫什麼、decorator vs 繼承 | 結構型 | ↓ Structural |
| 怎麼抽行為：strategy、狀態機、事件、undo/回放 | 行為型 | ↓ Behavioral |

貫穿鐵律：**pattern 是詞彙不是目標**——「用了幾個 pattern」不是品質指標；**先有痛，再上 pattern**（每個 pattern 的「進場訊號」沒出現就別上，YAGNI）。

## Creational（建立型）

| 何時 | 讀 |
|------|-----|
| new→factory→builder 進場階梯、abstract factory 何時、singleton 三宗罪與替代 | `references/creational-selection.md` |

## Structural（結構型）

| 何時 | 讀 |
|------|-----|
| adapter/facade/bridge 意圖裁決表、decorator vs 繼承、composite、proxy/flyweight | `references/structural-selection.md` |

## Behavioral（行為型）

| 何時 | 讀 |
|------|-----|
| strategy 進場訊號與函式化、FSM 三實作選型、observer 兩筆債、command 何時包 | `references/behavioral-selection.md` |
