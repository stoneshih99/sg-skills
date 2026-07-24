# Catastrophic backtracking 與 flavor 可攜性

regex「好慢」「卡死整個服務」幾乎都是同一個病：**catastrophic backtracking**。加上各語言 flavor 不一致，是把 regex 從別處抄來就爆的兩大原因。

## Catastrophic backtracking（ReDoS）

某些 pattern 對「快到匹配失敗」的輸入，回溯路徑會**指數爆炸**——幾十個字元就讓引擎跑幾秒到幾分鐘，CPU 打滿。若 pattern 或輸入來自使用者，這是一個 DoS 漏洞（**ReDoS**）。

**病灶：巢狀量詞、量詞重疊**——同一段輸入有多種被切分的方式：

```
(a+)+$        對 "aaaaaaaaaaX" → 引擎嘗試指數種 a 的分組方式才確定失敗
(a|a)*$       重疊的替代 → 同樣爆炸
(\d+)*$       量詞套量詞
.*.*=.*       多個貪婪 .* 互相搶 → 常見於「解析 key=value」的天真寫法
```

觸發條件：**量詞內的子式能以多種方式 match 同一段字元**，且整體最終 match 失敗（失敗才會窮盡所有回溯路徑）。

**怎麼發現**：pattern 裡有 `(…+)+`、`(…*)*`、`(a|ab)*`、相鄰多個 `.*`——就是嫌疑犯。用「一長串重複字元 + 一個讓它 match 失敗的結尾」測時間（`aaaa…!`），時間隨長度暴增就中了。

**修法**（由好到次）：
1. **消除歧義**：讓子式不重疊。`(a+)+` 其實等價於 `a+`——直接寫 `a+`。`.*.*=` 改成精確字元類 `[^=]*=`，每個字元只有一種歸屬。
2. **精確字元類取代 `.`**：`[^"]*` 之於 `.*`——沒有重疊就沒有回溯爆炸。
3. **atomic group / possessive 量詞**：`(?>a+)`、`a++`（PCRE/Java/Ruby/PHP 支援）——一旦 match 就不回退，直接切掉回溯路徑。**注意 JS、Python 舊版不支援**（見下方 flavor）。
4. **換非回溯引擎**：RE2（Go 內建、Rust regex、re2 綁定）保證線性時間、不支援 backreference/lookaround——處理**不可信輸入**時是最穩的選擇。
5. **設 timeout / 限長度**：.NET 的 `Regex` 可設 timeout；限制輸入長度是最後防線。

**鐵律**：**regex 碰不可信輸入時，要嘛用 RE2 類引擎、要嘛確保 pattern 無歧義並限長**——別把使用者輸入丟進一個有巢狀量詞的 PCRE。

## Flavor 可攜性：抄來的 pattern 不一定能跑

regex 不是一種語言，是一族方言。從 Stack Overflow / 別的語言抄 pattern 前，確認這些**不可攜**的點：

| 特性 | 情況 |
|------|------|
| **POSIX BRE vs ERE**（grep vs `grep -E`/egrep） | BRE 裡 `+ ? { } ( ) |` 要跳脫才有特殊義（`\+`、`\{`）；ERE 才是「現代」寫法。`sed` 預設 BRE。 |
| **lookaround**（`(?=)` `(?<=)`） | PCRE/JS/Python/Java 有；POSIX（grep/sed 預設）、RE2（Go）**沒有**。 |
| **backreference / 反向 lookbehind** | RE2 完全不支援 backreference；lookbehind 各家對「變長」支援不一（JS 支援變長、多數限定長）。 |
| **命名群組語法** | `(?<name>…)`（.NET/JS/Java）vs `(?P<name>…)`（Python）——語法不同。 |
| **`\d \w` 的 Unicode 語意** | 有些 flavor 預設 Unicode（`\d` match 全形/他國數字），有些預設 ASCII。要嚴格數字用 `[0-9]`，別賭 `\d`。 |
| **atomic group / possessive**（`(?>…)`、`a++`） | PCRE/Java/Ruby/PHP 有；**JS 沒有**，Python 3.11+ 才有。 |
| **flags 開法** | inline `(?i)`、`(?m)` 多數支援但位置規則不同；有的只能整串開頭。 |

**決策**：跨語言/工具搬 pattern，先問「目標引擎是哪族」（grep 用 `-E`？後端是 Go(RE2) 還是 Node(JS)？）。用到 lookaround/backreference 就**不能**丟給 RE2 或 POSIX grep。

## 常見坑

- **巢狀量詞 `(x+)+`**：catastrophic backtracking——化簡成 `x+` 或用精確字元類。
- **相鄰多個 `.*`**：`.*.*=.*` 爆炸——每字元給唯一歸屬 `[^=]*=`。
- **不可信輸入丟進 PCRE**：ReDoS DoS 漏洞——RE2 類引擎或無歧義 + 限長 + timeout。
- **抄來的 lookbehind/atomic 在 JS/Go 跑不動**：flavor 不支援——先確認目標引擎族。
- **`grep` 用 ERE 語法**：`grep 'a+'` 的 `+` 是字面——用 `grep -E` 或跳脫。
- **賭 `\d` 只 match 0-9**：Unicode 模式會更寬——嚴格就 `[0-9]`。
