# 交接 / 專案狀態

> 本檔記錄 monorepo 目前進度與下一步。撰寫規範見 [CONVENTIONS.md](CONVENTIONS.md)，主題歸屬見 [TOPIC-MAP.md](TOPIC-MAP.md)。

## 專案

`sg-skills`：Stone 的個人 Agent Skills marketplace，一個 repo 收三個正交 plugin。2026-07-24 由三個獨立 repo 合併而成。

| Plugin | 版本 | 結構 | 定位 |
|--------|------|------|------|
| **sg-game-dev-skills**（plugins/game-dev） | 0.21.3 | 5 hub / 80 篇 | 引擎中立遊戲（What/Why）。一人工作室的虛擬部門顧問團 |
| **sg-unity-dev-skills**（plugins/unity-dev） | 0.11.0 | 3 hub / 31 篇 | Unity 具體（How in Unity）。接住 game-dev 留白 |
| **sg-dev-skills**（plugins/dev） | 0.6.0 | 6 hub / 22 篇 | 通用工程（不限遊戲）。git / shell / Clean Code / 除錯方法論 / regex / CLI 設計 |

合計 14 hub、133 篇 reference。

## monorepo 合併（2026-07-24）

三個獨立 repo 合為一個 marketplace，理由：**個人自用，統一維護、防跨 plugin 重複設計**。

- 結構：`plugins/<x>/` 各是完整 plugin（自己的 plugin.json + skills/），頂層一個 `marketplace.json` 列三個 plugin（source 指向 plugins/*）。
- **關鍵技術現實**：安裝後每個 plugin 各自獨立快取，**跨 plugin 相對連結會斷**——跨 plugin 一律文字提及。monorepo 的真好處是：一份 CONVENTIONS、一張 TOPIC-MAP、一套 check-links、原子跨 plugin commit、一個 marketplace 一次加。
- 舊三 repo（github.com/stoneshih99/sg-{game-dev,unity-dev,dev}-skills）已刪除。
- 全新單一 git 歷史（未保留三 repo 舊 commit；舊 repo 刪除後歷史不再保存）。

## 驗證自動化（pre-commit hook）

改動後必跑的檢查已由 pre-commit hook 強制執行（「機器可查的進 hook」）：

- **`scripts/hooks/pre-commit`**（版控追蹤）：commit 前自動跑 `check-links.py` + `claude plugin validate .`，斷鏈或驗證失敗就擋下 commit。`claude` 不在 PATH 時自動略過 validate、連結檢查照跑。
- **掛法靠 `core.hooksPath`**（非 `.git/hooks/`，故進版控、重 clone 也在）。**重 clone 後跑一次**：`git config core.hooksPath scripts/hooks`。略過檢查用 `git commit --no-verify`。
- 兩條路徑都測過：正常 commit 通過、故意斷鏈 exit 1 擋下。

## Router 結論（跨 plugin 觸發）

三 plugin 共存**不需額外 router 層**——Claude Code 的 skill description 觸發本身就是 router。精準靠「description 邊界切乾淨 + 重疊詞用層區隔」。headless probe 驗證：跨 plugin 邊界全對、unity 三 hub sonnet 7/7；dev 六 hub 每加一 hub 都實裝 probe（git vs shell 6/6、+clean-code 6/6、+debug 7/7、+regex 6/7——1 題為 TOPIC-MAP 記錄的合理軟邊界、+cli 7/7，cli↔shell 零滲漏）。**相似 hub 用 sonnet 探測，別用 haiku**（haiku 對相同 query 會給不一致答案，曾誤導判斷）。

## 各 plugin 狀態

**game-dev**：五分類全開張，一分類一 hub。architecture 的 system（8 篇）與 net（4 篇）為實作決策級深度。既定候選全數完成，後續依實戰回饋擴充。

**unity-dev**：三 hub——unity-scripting（script/input/asset/test/editor）、unity-runtime（physics/net/shader/anim/audio/ui，6 家族/約 490 字元，再長考慮再拆）、unity-optimization（perf/build）。

**dev**：git-workflow（六域 8 篇）、shell-scripting（safety/text）、clean-code（naming/function/smell，語言中立可讀性/重構決策，不含風格慣例）、debug-methodology（process/locate/observe，通用除錯方法論；與 game-tooling 的 debug- 工具家族分層見 TOPIC-MAP）、regex-patterns（mechanics/safety/design，pattern 語言與坑；與 shell text- 的工具選型分層見 TOPIC-MAP）、cli-design（contract/interface/ux，設計行為良好的命令列程式；與 shell 的「寫腳本串工具」互補，見 TOPIC-MAP）。正交，routing 邊界最清楚。**六 hub 全於 2026-07-24 一日建成，既定候選（shell/clean-code/除錯方法論/regex/CLI）全數完成**，後續實戰需求驅動。

## 待辦

- [x] 三 repo 合併為 sg-skills monorepo，連結檢查 0 斷鏈、validate 通過、實裝 sonnet probe 5/5（2026-07-24）。
- [x] 舊三 repo 已刪除（2026-07-24）。
- [x] pre-commit hook 自動化連結檢查 + validate（2026-07-24）。
- [x] dev 加 debug-methodology hub（通用除錯方法論，2026-07-24）。
- [x] dev 加 regex-patterns hub（2026-07-24）。
- [x] dev 加 cli-design hub（2026-07-24）——**dev 既定候選全數完成**。
- [ ] 各 plugin 依實戰回饋擴充 references（三 plugin 皆無既定候選，實戰需求驅動）。
- [ ] unity-runtime 若再長，考慮 sub-split。

## 相關文件（歷史紀錄，重構時不回改）

- 各 plugin 原設計 spec/plan 未遷入 monorepo；舊 repo 已刪除，僅存於本機舊資料夾（如 `../sg-game-dev-skill/docs/superpowers/`）。
