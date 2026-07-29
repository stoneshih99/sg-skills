# 事件埋點設計

埋點的品質決定所有下游分析的上限。事後補埋救不回歷史資料，改 schema 會讓新舊資料不可比——所以埋點值得在 beta 前認真設計一次。

## 事件 Schema

每個事件 = **名稱 + 時間戳 + 玩家/裝置識別 + 參數**：

```
event: level_complete
timestamp: <UTC>
player_id: <匿名 id>
session_id: <本次遊玩>
params:
    level: "1-3"
    duration_sec: 245
    deaths: 2
    result: "win"       # win / quit / fail
context:                 # 全事件共通，SDK 自動帶
    game_version: "0.9.2"
    platform: "android"
```

設計原則：

- **共通欄位自動帶**：版本、平台、session_id 由發送層統一附加，不靠每個埋點手寫（漏一個就少一個維度）。
- **參數帶足上下文**：`level_complete` 不帶關卡編號等於白記——分析時第一個 group by 就是它。原則同日誌的屍檢思維（見 `debug-logging.md`）。
- **列舉值用固定字串**：`result: "win"/"quit"/"fail"` 事先定義，不要自由文字。
- **Schema 進版控**：事件定義寫成文件（或直接是資料表，見 config-driven 精神），埋點照文件實作，改動走 review——這份文件同時就是分析者的資料字典。

## 命名規範

- `名詞_動詞過去式` 或 `域_行為`：`level_start` / `level_complete` / `item_purchased` / `tutorial_step_done`。
- 全小寫 + 底線，一開始就定死——`LevelComplete`、`level-complete`、`levelcomplete` 混用會讓查詢痛苦終身。
- 同一域共用前綴（`shop_opened`、`shop_item_viewed`、`shop_purchase`），報表按前綴分組。

## 核心事件清單（建案照抄）

**生命週期**
- [ ] `session_start` / `session_end`（帶時長）——一切 session 指標的基礎。
- [ ] `game_version` 首啟 / 更新事件。

**進度（漏斗的原料）**
- [ ] `tutorial_step_done`（帶步驟編號）——新手漏斗最細粒度。
- [ ] `level_start` / `level_complete`（帶關卡、時長、死亡數、結果）。
- [ ] 里程碑事件：首次通關、解鎖大功能、劇情章節。

**經濟（配 `../../game-design/references/gdd-progression-economy.md` 的 source/sink 表）**
- [ ] `currency_earned` / `currency_spent`（帶來源/用途、數量、餘額）——通膨監控的原料。
- [ ] `item_purchased`（帶道具、價格、購買當下等級）。

**挫折訊號**
- [ ] `player_death`（帶位置、死因）——熱區圖找難度尖刺。
- [ ] `level_quit`（帶進度百分比）——rage quit 偵測。
- [ ] `crash` / `error`（帶版本與摘要）。

**（若有）變現**
- [ ] `iap_initiated` / `iap_completed`——分開記，兩者之差是付款流失。

## 隱私紅線

- **匿名識別**：player_id 用隨機生成的匿名 id，不用裝置序號/帳號 email。
- **不記個資**：姓名、email、精確位置、輸入的自由文字，一律不進遙測。
- **合規基本盤**：告知與同意（隱私政策）、提供退出選項、遵守目標市場法規（GDPR/兒少相關）。上架平台會審這個。
- 與 `debug-logging.md` 的敏感資訊規則同源：遙測資料會離開玩家裝置，標準更嚴。

## 常見陷阱

- **什麼都記**：事件爆量、儲存與查詢成本飆升、真正要用的欄位反而缺。從「要回答的問題」反推。
- **只記成功不記失敗**：有 `level_complete` 沒 `level_quit`，漏斗只看得到倖存者。
- **改 schema 不留版本**：參數意義悄悄改變，跨版本比較全錯。schema 變更記錄在資料字典。
- **埋點沒測試**：上線才發現某事件根本沒發或參數是空的。埋點驗證進 QA 清單（開發模式印出所有發送事件即可肉眼驗）。
