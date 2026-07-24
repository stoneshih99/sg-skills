# CLI 的 I/O 契約

一個 CLI 能不能被 pipe、被 script、被自動化，取決於它遵不遵守 Unix 的 I/O 契約。違反契約的工具「手動跑起來很好」，一放進 pipeline 就壞。這篇是那份契約。

## stdout 放資料，stderr 放其他一切

**這是最常被違反、後果最嚴重的一條**：

- **stdout（標準輸出）= 程式的「成果資料」**——會被下一個管道 `|` 吃掉、被 `>` 重導存檔的東西。只放真正的輸出。
- **stderr（標準錯誤）= 給人看的一切**：錯誤、警告、進度、log、診斷訊息。

為什麼：`mytool | grep x` 時，進度條/「處理中…」若印到 stdout 會污染資料、被 grep 當成資料處理。把它們放 stderr，資料流乾淨、訊息照樣顯示在終端機。

```
# 對：資料 → stdout，訊息 → stderr
echo "$result"          # stdout（會被 pipe/重導）
echo "處理完成" >&2     # stderr（給人看，不進管道）
```

**判準**：問「這行輸出，下一個程式該吃嗎？」該→stdout；只是給人看的→stderr。

## exit code：0 成功，非 0 分類失敗

呼叫者（script、CI、pipeline）靠 exit code 判斷成敗——**不是靠 parse 你的文字輸出**：

- **0 = 成功**，非 0 = 失敗。這讓 `mytool && next`、`set -e`、CI 判定能運作（見 shell-scripting 的 `set -e`）。
- **用不同非 0 值分類錯誤**：慣例上 1 = 一般錯誤、2 = 用法/參數錯誤；可自訂更多（找不到=3、權限=4…）並寫進 --help。有意義的 code 讓 script 能分流處理。
- **絕不「印錯誤訊息但 exit 0」**——這是最惡毒的坑：呼叫者以為成功，pipeline 帶著壞資料繼續。錯誤必須非 0。
- 遵守既有慣例：被訊號中止時 exit `128+signal`（Ctrl-C = 130）。

## 吃 stdin，成為 filter

能從 **stdin 讀**的工具才能放進管道中間（`cat data | mytool | next`）：

- 若工具處理「一份輸入資料」，支援兩種來源：**檔名參數**與**stdin**（無檔名參數時讀 stdin）。
- 慣例：用 `-` 當檔名代表 stdin/stdout（`mytool -` 從 stdin 讀）。
- 這讓你的工具變成可組合的 filter，而不是只能自己單獨跑的孤島。

## 機器可讀 vs 人看

同一份資料，終端機前的人和 pipeline 裡的程式要的格式不同：

- **預設輸出要能被機器處理**：穩定、逐行、欄位可切（給 grep/awk/cut）。花俏的表格框線、對齊空白讓程式難 parse。
- **提供結構化輸出選項**：`--json`（或 `--format`）給需要精確 parse 的呼叫者——比讓他們 regex 你的人類輸出穩得多（見 regex hub：別逼人 parse 半結構化文字）。
- 別在預設輸出裡混入「Found 3 results:」這種裝飾——那是給人的訊息，放 stderr 或 `--verbose`。

## 靜默即成功（沉默原則）

Unix 傳統：**成功時沒消息就是好消息**。一個成功的操作預設不該吐一堆「正在做…做完了…」到 stdout。

- 需要囉嗦時用 `--verbose`/`-v` 讓使用者主動要；需要更安靜用 `--quiet`/`-q`。
- 這不是冷漠，是尊重 pipeline：沉默的工具好組合，聒噪的工具製造噪音。

## 常見坑

- **進度/log 印到 stdout**：污染管道資料——所有非資料訊息 → stderr。
- **錯誤卻 exit 0**：呼叫者誤判成功、帶壞資料前進——錯誤必須非 0。
- **靠 parse 文字判斷成敗**：脆弱——用 exit code。
- **只能吃檔名不吃 stdin**：無法放進管道中間——支援 stdin 與 `-`。
- **預設輸出是花俏表格**：程式難 parse——預設機器友善，人看的裝飾另開 flag。
- **逼呼叫者 regex 你的輸出**：提供 `--json`。
- **成功時洗一堆訊息到 stdout**：噪音——沉默原則 + `--verbose` 才囉嗦。
