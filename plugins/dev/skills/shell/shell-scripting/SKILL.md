---
name: shell-scripting
description: shell 腳本與命令列的實作決策與坑——兩家族：可靠腳本（set -euo pipefail、quoting 防 word splitting、[[ ]] vs [ ]、trap 清理、變數展開、何時該從 shell 換成真語言）、文字處理（grep/sed/awk/cut/sort/jq 選型、find + xargs 防空格、pipeline 與 pipefail 坑）。當要寫 bash 腳本、串 pipeline、處理文字/log、「shell 腳本有時壞掉」「檔名有空格就爆」「grep/sed/awk 該用哪個」，或問「這段 shell 怎麼寫才穩」時使用。實作決策級，不是 shell 教學。
---

# Shell 腳本（Shell Scripting）

> **定位**：shell 腳本與命令列的**實作決策與坑**——「怎麼寫才穩、哪個工具、什麼時候該換語言」。不是 shell 教學（`ls`/`cd` 怎麼用，Claude 已知）。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 寫可靠的 bash 腳本、避免壞掉 | 可靠腳本 | ↓ Safety |
| 處理文字/log、grep/sed/awk/jq、pipeline | 文字處理 | ↓ Text |

貫穿鐵律：**變數永遠加引號 `"$var"`**（不加就是空格/glob 炸彈）；**shell 是黏合膠水不是程式語言**——超過它舒適區就換真語言（見 `references/safety-robust-scripts.md`）。

## Safety（可靠腳本）

| 何時 | 讀 |
|------|-----|
| 寫穩健 bash：set -euo pipefail、quoting、[[ ]]、trap 清理、變數展開、何時換語言 | `references/safety-robust-scripts.md` |

## Text（文字處理）

| 何時 | 讀 |
|------|-----|
| grep/sed/awk/cut/sort/jq 選型、find + xargs、pipeline 坑 | `references/text-processing.md` |
