---
name: regex-patterns
description: regex／正則表達式的實作決策與坑——跨語言中立：貪婪 vs 惰性、anchor 與邊界、群組與 backreference、catastrophic backtracking／ReDoS、flavor 可攜性（POSIX/PCRE/JS/Python）、何時該用 regex vs parser。當寫/讀 regex、「match 太多太貪婪」「這 pattern 為什麼不對」「regex 好慢/卡死」「跳脫怎麼處理」「各語言 regex 不一樣」「能不能用 regex 解析 HTML」時使用。決策/坑級，不是符號速查表。
---

# Regex／正則表達式

> **定位**：regex 的**決策與坑**——「為什麼 match 太多、為什麼卡死、這 flavor 能不能用、該不該用 regex」。不是符號速查（`\d`=數字這種背了就會，Claude 已知）。與 shell 的 `text-processing`（grep/sed/awk **工具選型**與 pipeline）分層：pattern 語言本身的問題在這裡，選哪個工具跑在那裡。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| match 太多/太少、貪婪、anchor、群組、跳脫、pattern 不對 | 機制與坑 | ↓ Mechanics |
| regex 卡死/好慢、ReDoS、各語言 regex 不一樣 | 安全與 flavor | ↓ Safety |
| 該不該用 regex、能不能 parse HTML、regex 太長讀不懂 | 設計 | ↓ Design |

貫穿鐵律：**預設貪婪會吃過頭**——量詞預設盡量多吃，`.*` 常一路吃到行尾；先想清楚要不要惰性或更精確的字元類。**能明確就別用 `.`**——用具體字元類縮小 match 面，同時避開回溯地雷。

## Mechanics（機制與坑）

| 何時 | 讀 |
|------|-----|
| 貪婪 vs 惰性、anchor/\b 邊界、字元類、capture/非捕獲/命名群組、backreference、over-match | `references/mechanics-and-pitfalls.md` |

## Safety（安全與 flavor）

| 何時 | 讀 |
|------|-----|
| catastrophic backtracking／ReDoS 與修法、不可信輸入、POSIX/PCRE/JS/Python flavor 可攜性 | `references/safety-backtracking-and-flavors.md` |

## Design（設計）

| 何時 | 讀 |
|------|-----|
| regex vs 字串函式 vs parser、別 parse HTML/巢狀、可讀性（x/verbose、命名群組、拆解）與測試 | `references/design-when-and-readability.md` |
