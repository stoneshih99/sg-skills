# 寫可靠的 bash 腳本

Shell 腳本「有時壞掉」「檔名有空格就爆」幾乎都是幾個固定的坑。這篇是把 bash 腳本從脆弱變可靠的紀律，以及「什麼時候該放棄 shell」。

## 開頭三件套：`set -euo pipefail`

```bash
#!/usr/bin/env bash
set -euo pipefail
```

各自防什麼（缺一個就有一類坑）：

- **`set -e`**：任何指令失敗（非零退出）就中止——不加的話，錯誤指令後腳本繼續跑，用著壞掉的狀態（例：`cd /notexist` 失敗但後面 `rm -rf *` 照跑在錯的目錄）。
- **`set -u`**：用未定義變數就報錯——不加的話，`rm -rf "$DIR/"` 在 `DIR` 沒設時變成 `rm -rf /`（打字錯的變數名靜默變空字串）。
- **`set -o pipefail`**：pipeline 中任何一段失敗就算失敗——不加的話 `false | true` 回傳成功，`grep x file | sort` 的 grep 失敗被 sort 的成功蓋掉。

**注意 `set -e` 的例外**：某些情況 `-e` 不觸發（在 `if`/`||`/`&&` 條件中、函式被條件呼叫時）——複雜腳本別完全依賴 `-e`，關鍵處顯式檢查 exit code。

## Quoting：最常見的坑

**變數展開一律加雙引號 `"$var"`**——不加就發生 word splitting（空格拆成多個參數）與 glob 展開（`*` 被展開）：

```bash
file="my file.txt"
rm $file          # 錯：拆成 rm "my" "file.txt" → 刪錯檔或報錯
rm "$file"        # 對

for f in "$@"     # 對：保留參數邊界（$@ 加引號才正確）
"${array[@]}"     # 對：陣列展開加引號
```

- **`"$@"` 不是 `$*`**：`"$@"` 保留每個參數的邊界，`$*` 併成一個字串——傳參一律 `"$@"`。
- **命令替換也加引號**：`"$(cmd)"`——除非你明確要 word splitting。
- 工具檢查：**ShellCheck** 抓 quoting 與大部分 shell 坑——腳本過 ShellCheck 是基本盤（等同 shell 的 lint）。

## `[[ ]]` 而非 `[ ]`

```bash
if [[ "$x" == "yes" && -f "$file" ]]; then    # 用 [[ ]]
```

- **`[[ ]]`（bash 內建）**優於 `[ ]`（test 指令）：不需要對變數加引號也較安全、支援 `&&`/`||`/`==` 模式匹配/`=~` 正則。
- `[ ]` 是舊 POSIX，變數沒引號會炸（空值/空格）——bash 腳本用 `[[ ]]`。

## 變數展開的預設與檢查

```bash
"${var:-default}"     # var 未設或空 → 用 default
"${var:?訊息}"        # var 未設或空 → 報錯中止（必填參數檢查）
"${var:=default}"     # 未設 → 設為 default 並用
"${1:?用法: script <arg>}"   # 必填位置參數
```

## trap：清理與退出處理

```bash
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT      # 不論正常/錯誤/中斷退出都清理暫存
```

- **EXIT trap 做清理**：暫存檔、鎖、背景程序——不論怎麼退出都執行（比手動在每個退出點清乾淨）。
- `trap ... INT TERM` 處理中斷訊號。

## 何時該放棄 shell（重要判斷）

**shell 是黏合膠水，不是程式語言**——這些信號代表該換 Python/其他：

- 需要**資料結構**（巢狀、關聯陣列超過簡單用法、JSON 處理）——shell 硬做很痛。
- 需要**真的錯誤處理**（try/catch、結構化例外）。
- 腳本**超過 ~50-100 行**、有複雜邏輯分支。
- 需要**可測試**（shell 難單元測試）。
- 大量**浮點數學**（shell 只有整數，要 `bc`/`awk` 繞）。

**判準**：如果你在 shell 裡實作資料結構或複雜控制流，你是在用錯工具——換語言比把 shell 寫得更聰明便宜。

## 常見坑

- **變數不加引號**：word splitting + glob，檔名有空格就炸——一律 `"$var"`（ShellCheck 抓）。
- **沒 set -euo pipefail**：錯誤靜默、未定義變數變空、pipeline 失敗被吞。
- **`rm -rf "$DIR/"` 沒防空值**：`DIR` 空 → `rm -rf /`——`set -u` + `"${DIR:?}"`。
- **用 `[ ]` 不加引號**：空值/空格炸——用 `[[ ]]`。
- **暫存檔不清**：腳本中斷留垃圾——trap EXIT。
- **在 shell 裡蓋大樓**：500 行 bash 實作業務邏輯——換語言。
- **parse `ls` 輸出**：檔名有特殊字元就壞——用 glob 或 `find -print0`（見 `text-processing.md`）。
