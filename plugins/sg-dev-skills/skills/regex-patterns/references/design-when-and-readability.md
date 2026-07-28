# 何時該用 regex，以及怎麼寫得能維護

regex 強大到容易被濫用。一半的 regex 問題不是「pattern 錯」，是「根本不該用 regex」或「寫成一條沒人看得懂的天書」。這篇是這兩個決策。

## 何時用 regex、何時別用

regex 適合**在文字裡找/切/換符合某個 pattern 的片段**。判斷該不該用：

| 你要做的 | 用什麼 |
|----------|--------|
| 固定字串包含/開頭/結尾/取代 | **字串函式**（`contains`/`startsWith`/`replace`）——比 regex 快、清楚、不用跳脫 |
| 固定分隔符切欄位 | **split**，不是 regex |
| 找/驗證/抽取有 pattern 的片段（email 樣式、log 行、版本號） | **regex** ← 甜蜜點 |
| 解析**巢狀/遞迴**結構（HTML、JSON、程式碼、括號配對） | **專用 parser**，不是 regex |
| 有現成 parser 的格式（URL、日期、CSV、JSON） | **該格式的函式庫**，別自己 regex |

**鐵律：別用 regex 解析 HTML/XML/巢狀結構**。正則語言在數學上無法可靠匹配任意巢狀（配對的括號/標籤）——你能寫出對 90% 輸入有效的 pattern，但剩下 10% 會靜默錯，而且越補越脆。用 DOM/HTML parser。

**判準**：資料是「扁平、有規律的文字」→ regex 合適；「有結構、會巢狀、有既定格式」→ 用 parser/函式庫。regex 是掃描器不是解析器。

## 別追求「一條 regex 解決」

把整個驗證/抽取塞進一條 200 字元的 regex，是可讀性與可維護性災難——沒人（包括三個月後的你）改得動、測不出哪段錯。

**拆解優於巨獸**：
- 用**多個小 regex + 一般程式邏輯**串起來，通常比一條巨獸清楚、好測、好改。先 split 成行/欄，再各自用小 pattern。
- 先做粗篩（regex）再做精確驗證（程式碼/函式庫）——例如 email：regex 抓「像 email 的東西」，真正驗證交給 email 函式庫或發驗證信。

## 寫得能維護

- **verbose / extended 模式（`x` flag）**：允許在 pattern 裡加**空白與註解**，把長 pattern 分行、每段標註用途。一條密碼般的 pattern 拆成帶註解的多行，可讀性天差地別（支援度：PCRE/Python/Java/.NET 有，JS 需靠樣板字串自行拼）。
- **命名群組**（見 `mechanics-and-pitfalls.md`）：`(?<year>…)-(?<month>…)` 比 `$1-$2` 自我說明，且改 pattern 不錯位。
- **具名常數**：把 pattern 存成有名字的常數/變數（`EMAIL_LIKE = /…/`），別在邏輯裡散落字面 regex——同 Clean Code 的魔術數字原則（見 dev 的 clean-code hub）。
- **一定要測**：regex 是 write-once-read-never 的重災區。對它寫測試——尤其**邊界與該失敗的案例**（空字串、超長、該拒絕的輸入、Unicode）。ReDoS 測試（超長重複輸入）也放進來（見 `safety-backtracking-and-flavors.md`）。
- **附一個範例**：pattern 旁邊註解一兩個 match/不 match 的例子，讀的人不用在腦中執行引擎。

## 常見坑

- **固定字串也用 regex**：`replace(/foo/, …)` 而非 `replace("foo", …)`——慢、要跳脫、沒必要。
- **regex parse HTML/巢狀**：數學上做不到可靠——用 parser。
- **自己 regex 解析 URL/日期/CSV**：有現成函式庫且處理好邊界——別重造。
- **一條巨獸 regex**：不可讀不可測——拆成小 regex + 程式邏輯。
- **字面 regex 散落程式各處**：改一處漏一處——具名常數集中。
- **沒測 regex**：邊界/該失敗案例最會出錯——寫測試含 Unicode 與 ReDoS 輸入。
