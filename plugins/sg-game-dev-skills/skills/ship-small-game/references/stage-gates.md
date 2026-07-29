# Stage Gates

## Preflight

- 進入條件：收到遊戲構想或既有專案的交付請求。
- 必做工作：讀取 repository 指令與既有文件，盤點引擎、平台、工具、資產授權、測試與 Build 能力。
- 核准閘門：確認現況、限制與未知項已記錄。
- 完成證據：專案盤點與可用證據寫入交付物。
- 下一階段：Game Contract。

## Game Contract

- 進入條件：Preflight 已完成，專案現況可被追溯。
- 必做工作：定義產品承諾、目標玩家、平台、核心循環、起訖流程與範圍。
- 核准閘門：核心玩法、範圍、平台與重大決策獲得核准。
- 完成證據：已核准的 game brief。
- 下一階段：Production Blueprint。

## Production Blueprint

- 進入條件：Game Contract 已核准。
- 必做工作：拆分工作包、依賴、驗證方式、風險與階段計畫。
- 核准閘門：排程、技術選型與交付順序可執行。
- 完成證據：可追溯的 delivery roadmap 與 acceptance matrix。
- 下一階段：Vertical Slice。

## Vertical Slice

- 進入條件：Production Blueprint 已建立且核心工作包可開始。
- 必做工作：完成一段代表性內容，證明輸入、玩法、內容、視覺、測試與 Build 的端到端管線。
- 核准閘門：確認垂直切片證明端到端管線，且可作為後續量產基準。
- 完成證據：可執行的垂直切片 Build、流程證據與驗收結果。
- 下一階段：Content Complete。

## Content Complete

- 進入條件：Vertical Slice 已核准，量產範圍與管線可用。
- 必做工作：完成核准範圍內的玩法、內容、資產與流程，並關閉未完成工作包。
- 核准閘門：Content Complete 後停止新增功能；新增需求必須回到範圍核准。
- 完成證據：所有已核准內容在 acceptance matrix 中有狀態與證據。
- 下一階段：Quality Complete。

## Quality Complete

- 進入條件：Content Complete 已達成，沒有未核准的新功能。
- 必做工作：完成程式、完整流程、視覺、效能、存檔與玩測的驗證與修正。
- 核准閘門：剩餘 Blocked 項目與已接受風險獲得核准。
- 完成證據：程式／完整流程／視覺／效能／存檔／玩測皆有執行證據。
- 下一階段：Release Candidate。

## Release Candidate

- 進入條件：Quality Complete 已完成，僅保留核准風險。
- 必做工作：凍結候選版、執行最終驗收並整理交付資訊。
- 核准閘門：正式發佈、平台與已接受風險獲得核准。
- 完成證據：有可執行 Build，且最終驗收與版本資訊可追溯。
- 下一階段：交付或正式發佈。
