# 文字處理：工具選型與 pipeline

grep/sed/awk/cut/jq 各有擅長，選錯就是「用 sed 硬幹該用 awk 的事」或「grep 一堆管道串出 awk 一行的效果」。這篇是選型與 pipeline 的坑。

## 工具選型

| 工具 | 擅長 | 別拿它做 |
|------|------|---------|
| **grep** | 找/過濾符合模式的行 | 欄位提取（那是 cut/awk）、取代（那是 sed） |
| **cut** | 按分隔符/位置取欄位（簡單） | 多分隔符、需要邏輯（那是 awk） |
| **sed** | 行的**取代**（s///）、刪除、簡單編輯 | 多欄位計算、狀態（那是 awk） |
| **awk** | **欄位處理 + 邏輯 + 計算**（按欄位、條件、累加） | 巢狀資料（那是 jq/程式） |
| **sort/uniq** | 排序、去重、計數（`sort \| uniq -c`） | — |
| **jq** | **JSON** 查詢/轉換 | 非結構化文字（那是 grep/awk） |

**選型心法**：
- 找行 → **grep**；取簡單欄位 → **cut**；取代 → **sed**；欄位 + 邏輯 + 算 → **awk**；JSON → **jq**。
- **一個 awk 常取代一串 grep|cut|sed**：`grep x | awk '{print $2}'` 可以 `awk '/x/{print $2}'`——awk 能過濾又能取欄位。
- **UUOC（無用的 cat）**：`cat file | grep x` → `grep x file`——工具直接吃檔案，不用 cat 餵。

## awk 的甜蜜點

awk 是「文字的迷你程式語言」——過濾 + 欄位 + 累加一次搞定：

```bash
# 過濾 + 取欄位 + 條件
awk -F',' '$3 > 100 { print $1, $3 }' data.csv    # 第3欄>100 的印第1、3欄

# 累加/統計（sort|uniq 做不到的計算）
awk '{ sum += $2 } END { print sum }' file        # 加總第2欄

# 分組計數
awk '{ count[$1]++ } END { for (k in count) print k, count[k] }'
```

需要「按欄位 + 條件 + 累加/分組」時，awk 一行勝過一串管道。

## find + xargs：批次處理的坑

```bash
# 錯：檔名有空格/換行就炸
find . -name "*.log" | xargs rm

# 對：-print0 + -0 用 null 分隔（防空格/特殊字元）
find . -name "*.log" -print0 | xargs -0 rm

# 或 find 直接 -exec（不用 xargs）
find . -name "*.log" -exec rm {} +               # {} + 批次；{} \; 逐個
```

- **`-print0` / `-0`**：檔名可能有空格、換行、特殊字元——用 null 分隔才安全（同 `safety-robust-scripts.md` 的 quoting 精神）。
- **`-exec {} +` vs `{} \;`**：`+` 把多個檔案一次傳給指令（快）、`\;` 每個檔案跑一次（慢但有時必要）。
- **別 parse `ls`**：`ls` 輸出給人看，檔名特殊字元會壞——用 glob（`*.log`）或 `find`。

## Pipeline 的坑

- **pipefail**：pipeline 中間段失敗預設被最後一段的成功蓋掉——`set -o pipefail`（見 `safety-robust-scripts.md`）讓任何段失敗都算失敗。
- **subshell 變數不外傳**：`cmd | while read x; do count=$((count+1)); done` 的 `count` 在 subshell 裡，迴圈結束就沒了——用 process substitution `while read x; do ...; done < <(cmd)` 或改結構。
- **grep 找不到 = 非零退出**：在 `set -e` 下 `grep x file` 找不到會中止腳本——預期可能找不到時 `grep x file || true`。
- **緩衝**：pipeline 中 grep/sed 有緩衝，即時輸出（如 tail -f | grep）要 `grep --line-buffered`。

## 常見坑

- **grep|cut|sed 一長串**：多半一個 awk 搞定——會 awk 省很多管道。
- **find|xargs 沒 -print0**：檔名有空格就炸——`-print0 | xargs -0`。
- **parse ls**：特殊字元壞——用 glob/find。
- **while read 在 pipe 裡改變數**：subshell 不外傳——`< <(cmd)` process substitution。
- **grep 找不到中止腳本**：`set -e` + grep 非零——`|| true`。
- **cat file | ...**：UUOC——工具直接吃檔案。
- **用 sed 做多欄位邏輯**：硬幹——那是 awk 的事。
