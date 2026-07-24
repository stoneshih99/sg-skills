# CLI 的 UX：help、錯誤訊息、TTY、破壞性操作

CLI 的 UX 不是花俏，是**在使用者卡住的瞬間給對資訊**：不會用時的 help、出錯時的訊息、誤操作前的防護。這篇是這三個時刻的設計。

## --help：第一個接觸點

使用者不讀文件，讀 `--help`。好的 help 結構：

```
用一句話說這工具做什麼

USAGE:
  tool [FLAGS] <FILE>

EXAMPLES:            ← 最重要的段落：常見用法直接可抄
  tool data.csv
  cat data.csv | tool --json

FLAGS:
  -o, --output <PATH>   輸出位置（預設 stdout）
  ...
```

- **範例優先**：多數人是抄範例改，不是讀旗標表——放 2-3 個最常見用法。
- 第一行講「做什麼」，不是版本宣告。
- `-h` 給精簡版、`--help` 可以更長；沒有參數又必須有參數時，印簡短 usage 到 **stderr** 並 exit 2（見 `contract-io-and-exit.md`）。
- help 印到 **stdout**（使用者主動要的資料，會想 `--help | grep`）。

## 錯誤訊息：說了什麼壞 + 怎麼修

錯誤訊息的品質決定使用者卡多久。公式：**發生了什麼 + 為什麼 + 下一步**：

```
壞：Error: operation failed          ← 什麼都沒說
好：error: 無法讀取 config.toml（第 12 行：duplicate key "port"）
    移除重複的 "port" 或用 --config 指定其他檔案
```

- **具體**：哪個檔、哪行、哪個值——你程式裡明明知道，別吞掉。
- **可行動**：能建議修法就建議（「did you mean `--output`?」對打錯旗標特別有效）。
- **人話**：別把 stack trace 當錯誤訊息丟給使用者（`--verbose`/debug 模式才給完整 trace）。
- 印到 **stderr**、exit 非 0（契約見 `contract-io-and-exit.md`）。

## TTY 偵測：互動與非互動是兩個世界

**輸出是給人（終端機）還是給程式（pipe/重導）？用 isatty 偵測，行為要不同**：

| | stdout 是 TTY（人在看） | 不是 TTY（pipe/檔案/CI） |
|--|----------------------|------------------------|
| 顏色 | 可以有 | **關**（否則下游吃到 ANSI 碼：`\x1b[32m` 污染資料） |
| 進度條/spinner | 可以有 | 關（log 檔裡的進度條是災難） |
| 表格對齊/裝飾 | 可以有 | 改機器友善格式 |
| 互動提問 | 可以問 | **不能問**（CI 裡卡死等輸入）——改用旗標或報錯 |

- **尊重 `NO_COLOR` 環境變數**與 `--no-color` 旗標；也提供 `--color=always` 給「pipe 給 less -R」的人。
- **非互動環境絕不 prompt**：stdin 不是 TTY 時，需要確認的操作應該失敗並提示用 `--yes`——而不是掛在那等一個永遠不會來的輸入（CI 最常見的卡死原因）。

## 訊號與中斷：Ctrl-C 要乾淨

- **Ctrl-C（SIGINT）要能停**，且停得乾淨：清暫存檔、恢復終端機狀態、rollback 做一半的操作（同 shell-scripting 的 trap 清理精神）。
- 長時間操作考慮「第一次 Ctrl-C 優雅收尾、第二次立即退出」。
- exit code 用 130（128+SIGINT），讓呼叫的 script 知道是被中斷不是失敗。

## 破壞性操作：預設安全

會刪除/覆寫/不可逆的操作，防呆是設計責任不是使用者責任：

- **`--dry-run`**：先看會發生什麼，不真做——批次/破壞性工具的標配。
- **確認機制**：互動時 prompt 確認；非互動要求明確 `--yes`/`--force`——**別讓 CI 裡的一次呼叫默默刪光**。
- 高風險操作可要求輸入目標名稱確認（如「輸入專案名以確認刪除」）。
- 能可逆就可逆：進垃圾桶而非直接刪、留 backup、輸出「怎麼復原」的提示。
- **預設值永遠是安全那邊**（見 `interface-flags-and-args.md`）：`--force` 才覆寫，不是 `--no-clobber` 才不覆寫。

## 常見坑

- **help 沒範例**：使用者要自己拼旗標——EXAMPLES 段放最常見用法。
- **錯誤訊息只說 failed**：不說哪裡、為何、怎麼修——三段公式。
- **stack trace 直接糊臉**：人話摘要 + `--verbose` 才給 trace。
- **pipe 進檔案還帶 ANSI 色碼**：污染資料——isatty 偵測 + NO_COLOR。
- **CI 裡 prompt 卡死**：stdin 非 TTY 就不問——報錯提示 `--yes`。
- **Ctrl-C 留一地暫存/爛狀態**：訊號處理 + 清理。
- **破壞性操作零確認**：一個 typo 刪光——dry-run + 非互動要 `--yes`。
