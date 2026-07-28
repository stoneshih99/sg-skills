---
name: cli-design
description: 設計/寫命令列程式的實作決策與坑——語言中立，三家族：I/O 契約（stdout 放資料、stderr 放訊息與錯誤、exit code 分類、吃 stdin 能被 pipe、機器可讀 --json vs 人看）、介面（args vs flags/options、短長旗標與 -h/--help/--version/`--`/`-` 慣例、子命令、設定優先序 flag>env>檔>預設、常見情況免旗標）、UX（好的 --help、錯誤訊息說原因+怎麼修、TTY 偵測顏色/進度、NO_COLOR、Ctrl-C 乾淨結束、破壞性操作 --dry-run/--yes）。當要寫命令列工具、「我的 CLI 怎麼設計」「要能被 pipe/script」「exit code/stderr 怎麼處理」「flag 怎麼設計」「該不該上色」時使用。設計/坑級，不是特定工具用法教學。
---

# CLI 設計（Command-Line Tool Design）

> **定位**：**寫一個行為良好的命令列程式**的決策與坑——I/O 契約、介面慣例、UX。不是「某個工具怎麼用」的教學（那是工具文件）。與 shell 的 `shell-scripting` 互補：那邊寫**腳本串工具**，這邊設計**被腳本呼叫的那個工具**——你的 CLI 遵守契約，別人的腳本才串得動它。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 輸出放哪、exit code、能不能被 pipe、機器可讀 | I/O 契約 | ↓ Contract |
| 參數 vs 旗標、子命令、--help/--version、設定優先序 | 介面 | ↓ Interface |
| help 怎麼寫、錯誤訊息、要不要上色/進度、破壞性操作 | UX | ↓ UX |

貫穿鐵律：**你的 CLI 是別人 pipeline 裡的一節**——設計時假設它的輸出會被另一個程式吃、被 script 呼叫、在非互動環境跑。**能被組合 > 功能華麗**（Unix 哲學：做好一件事、吃 stdin 吐 stdout、沉默即成功）。

## Contract（I/O 契約）

| 何時 | 讀 |
|------|-----|
| stdout/stderr 分工、exit code 分類、吃 stdin 能被 pipe、機器可讀 vs 人看、靜默原則 | `references/contract-io-and-exit.md` |

## Interface（介面）

| 何時 | 讀 |
|------|-----|
| args vs flags/options、短長旗標與 `-h`/`--version`/`--`/`-` 慣例、子命令、設定優先序、預設值 | `references/interface-flags-and-args.md` |

## UX（使用者體驗）

| 何時 | 讀 |
|------|-----|
| 好的 --help、錯誤訊息（原因+怎麼修）、TTY 偵測顏色/進度、NO_COLOR、訊號處理、--dry-run/--yes | `references/ux-help-errors-and-tty.md` |
