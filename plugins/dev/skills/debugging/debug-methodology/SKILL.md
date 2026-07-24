---
name: debug-methodology
description: 通用除錯方法論的實作決策與坑——語言/領域中立的「怎麼找 bug」，三家族：系統流程（可靠重現→觀察→假設→一次只改一變數→驗證 root cause 不是症狀；反模式：亂槍打鳥、修症狀）、定位（空間二分／時間二分 git bisect／最小重現／差異除錯 works-here-not-there）、觀察訊號（讀 stack trace 與錯誤而非猜、log vs debugger vs print 取捨、該埋哪、flaky/race/heisenbug）。當在找 bug、「重現不出來」「stack trace 看不懂」「改了沒用」「時好時壞/flaky」「該加 log 還是開 debugger」「怎麼定位是哪裡壞」時使用。方法論/決策級，不是特定語言除錯器教學、不是遊戲除錯工具（那是 game-tooling）。
---

# 通用除錯方法論（Debug Methodology）

> **定位**：語言/領域中立的**除錯決策**——「怎麼可靠重現、怎麼定位、怎麼讀失敗訊號、卡住時怎麼辦」。不是特定除錯器的按鈕教學，也不是遊戲用的除錯工具（debug draw／作弊碼／時間控制屬 game-tooling 的 debug- 家族）。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 從哪下手、整個除錯流程怎麼走、一直卡住 | 系統流程 | ↓ Process |
| 定位是哪裡／哪個 commit／哪個輸入壞的 | 定位 | ↓ Locate |
| 讀 stack trace、該加 log 還是 debugger、flaky/race | 觀察訊號 | ↓ Observe |

貫穿鐵律：**先可靠重現，再動手**——重現不了就先解決重現；**一次只改一個變數**——同時改多處，好了也不知道是誰治好的；**找 root cause 不是修症狀**——症狀修掉會從別處冒出來。

## Process（系統流程）

| 何時 | 讀 |
|------|-----|
| 科學方法式除錯：重現→假設→驗證、root cause vs 症狀、卡住時的解法、反模式 | `references/process-scientific-method.md` |

## Locate（定位）

| 何時 | 讀 |
|------|-----|
| 空間二分（切一半）/時間二分（git bisect）/最小重現/差異除錯，何時用哪個 | `references/locate-narrowing-down.md` |

## Observe（觀察訊號）

| 何時 | 讀 |
|------|-----|
| 讀 stack trace 與錯誤、log vs debugger vs print 取捨、埋在哪、flaky/race/heisenbug | `references/observe-reading-signals.md` |
