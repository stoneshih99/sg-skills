---
name: game-diagrams
description: 畫遊戲開發常用圖表的參考。當要畫遊戲流程圖（畫面/場景導航）、狀態機圖（角色/AI/遊戲階段）、系統關係圖（系統相依與資料流）、經濟資源流圖（source/sink），或使用者說「畫個流程圖」「把這個系統畫出來」「幫我把循環視覺化」時使用。預設輸出 Mermaid（GitHub / Obsidian 可直接渲染），引擎中立。
---

# 遊戲開發圖表

把設計與架構「畫出來」：對的圖型讓討論從各說各話變成指著同一張圖。這個 skill 提供選圖邏輯與每種圖的 Mermaid 範式。

## 何時用

- 設計文件需要視覺化（企畫、關卡、系統設計的說明圖）。
- 討論卡在「你說的跟我想的不一樣」——先畫圖再吵。
- 交接 / review 時要快速讓人看懂系統結構。

## 選圖邏輯

問「你要表達的是什麼關係」，對照選型：

| 要表達的 | 圖型 | Reference |
|----------|------|-----------|
| 玩家在畫面 / 場景之間怎麼移動 | 遊戲流程圖 | `references/game-flow-diagram.md` |
| 一個東西在不同狀態間怎麼切換 | 狀態機圖 | `references/state-machine-diagram.md` |
| 系統之間誰依賴誰、資料怎麼流 | 系統關係圖 | `references/system-relation-map.md` |
| 資源從哪來、到哪去、會不會通膨 | 經濟資源流圖 | `references/economy-flow-diagram.md` |

分不清流程圖與狀態機：**主詞是玩家（在畫面間移動）→ 流程圖；主詞是物件（自身狀態切換）→ 狀態機**。

## 產出約定

1. **預設 Mermaid**，放在 fenced code block（```mermaid）中，任何 Markdown 環境可攜。
2. **一張圖一個問題**：圖回答不了單一句子描述的問題，就拆成多張。
3. **節點命名用領域詞**：`主選單`、`戰鬥中`、`結算`——不用 `state1`、`A`。
4. **先草後精**：先畫全貌粗圖對齊認知，需要細節再放大局部另畫一張。
5. 每篇 reference 含該圖型的 Mermaid 範式與畫法要點，照抄改名即可用。

## References

| 檔案 | 內容 | 何時讀 |
|------|------|--------|
| `references/game-flow-diagram.md` | 畫面 / 場景流：主選單到遊戲內的導航、覆蓋層、離開路徑 | 畫 UI / 場景導航時 |
| `references/state-machine-diagram.md` | 狀態機：角色動作、AI 行為、遊戲階段的狀態與轉移 | 畫狀態切換時 |
| `references/system-relation-map.md` | 系統關係：模組相依方向、資料流、分層 | 畫架構 / 交接圖時 |
| `references/economy-flow-diagram.md` | 資源流：source → 池 → sink、兌換關係、通膨檢查 | 畫經濟 / 資源設計時 |
