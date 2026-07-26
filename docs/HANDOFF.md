# 交接 / 專案狀態

> 本檔記錄 monorepo 目前進度與下一步。撰寫規範見 [CONVENTIONS.md](CONVENTIONS.md)，主題歸屬見 [TOPIC-MAP.md](TOPIC-MAP.md)。

## 專案

`sg-skills`：Stone 的個人 Agent Skills marketplace，一個 repo 收三個正交 plugin。2026-07-24 由三個獨立 repo 合併而成。

| Plugin | 版本 | 結構 | 定位 |
|--------|------|------|------|
| **sg-game-dev-skills**（plugins/game-dev） | 0.26.0 | 5 hub / 87 篇 | 引擎中立遊戲（What/Why）。一人工作室的虛擬部門顧問團 |
| **sg-unity-dev-skills**（plugins/unity-dev） | 0.16.1 | 3 hub / 36 篇 | Unity 具體（How in Unity）。接住 game-dev 留白 |
| **sg-dev-skills**（plugins/dev） | 0.7.1 | 7 hub / 25 篇 | 通用工程（不限遊戲）。git / shell / Clean Code / 除錯方法論 / regex / CLI 設計 / 設計模式 |

合計 15 hub、148 篇 reference。

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

**unity-dev**：三 hub——unity-scripting（script/input/asset/test/editor）、unity-runtime（physics/net/shader/anim/audio/ui/2d，7 家族、description 已超 ~400 字元準則，**再加家族前先拆 hub**）、unity-optimization（perf/build）。

**dev**：git-workflow（六域 8 篇）、shell-scripting（safety/text）、clean-code（naming/function/smell，語言中立可讀性/重構決策，不含風格慣例）、debug-methodology（process/locate/observe，通用除錯方法論；與 game-tooling 的 debug- 工具家族分層見 TOPIC-MAP）、regex-patterns（mechanics/safety/design，pattern 語言與坑；與 shell text- 的工具選型分層見 TOPIC-MAP）、cli-design（contract/interface/ux，設計行為良好的命令列程式；與 shell 的「寫腳本串工具」互補，見 TOPIC-MAP）、design-patterns（creational/structural/behavioral，pattern 選型與坑非教學；FSM/singleton/observer 三個 overlap 詞的跨 plugin 分工見 TOPIC-MAP）。正交，routing 邊界最清楚。**六 hub 全於 2026-07-24 一日建成，既定候選（shell/clean-code/除錯方法論/regex/CLI）全數完成**，後續實戰需求驅動。

## 待辦

- [x] 三 repo 合併為 sg-skills monorepo，連結檢查 0 斷鏈、validate 通過、實裝 sonnet probe 5/5（2026-07-24）。
- [x] 舊三 repo 已刪除（2026-07-24）。
- [x] pre-commit hook 自動化連結檢查 + validate（2026-07-24）。
- [x] dev 加 debug-methodology hub（通用除錯方法論，2026-07-24）。
- [x] dev 加 regex-patterns hub（2026-07-24）。
- [x] dev 加 cli-design hub（2026-07-24）——**dev 既定候選全數完成**。
- [x] unity-scripting 加 asset-save-persistence（存檔 Unity 落地；概念層 system-foundation 既有，TOPIC-MAP 補存檔裁決行，2026-07-25）。
- [x] game-production 開 platform- 家族（行動/PC 平台約束兩篇，新域故擴 hub description；TOPIC-MAP 補平台裁決行，2026-07-25）。
- [x] 2D/isometric 雙層：game-architecture 加 algo-2d-projection-and-grids（algo 既有家族）、unity-runtime 開 2d- 家族（新域擴 description）；TOPIC-MAP 補 2D 裁決行（2026-07-25）。
- [x] 美術資產生成三篇：art-asset-sourcing（AI/外包/資產包選型）、anim-2d-frames-vs-skeletal（逐幀 vs Spine 類骨骼）、unity anim-2d-spritesheet-and-skeletal（2D Animation vs Spine runtime）——全落既有家族，不動 description（2026-07-25）。
- [x] tile-based 雙層：game-production 加 art-tileset-tilemap-standards（tileset 規格/autotile 模板/層結構/編輯器選型）、unity-runtime 加 2d-tilemap-workflow（Rule Tile/Composite 碰撞/批次 API）；TOPIC-MAP 補 Tilemap 裁決行（2026-07-26）。
- [x] game-design 加 gdd-deconstruction（參考作拆解：五切面/兩輪紀律/三張表，gdd 既有家族；發想鏈缺口之一，另一缺口「量化市場調研」暫緩，2026-07-26）。
- [x] unity-runtime 加 net-fishnet-and-eos（FishNet v4 SyncVar<T>/Prediction v2/EOS P2P listen-server 架構真相；net 既有家族，description 的框架列舉補 FishNet 與 EOS，2026-07-26）。
- [x] dev 開 design-patterns hub（patterns 分類，creational/structural/behavioral 三篇；TOPIC-MAP 補邊界節與 overlap 詞分工，2026-07-26）。
- [x] design-patterns hub 的 sonnet probe：8 題 6/8（2026-07-26）。跨 plugin 邊界全對（FSM 遊戲 AI→game-architecture、事件系統設計→game-architecture）。兩個 miss 已處置：①「if-else 重複」落 clean-code＝合理軟邊界（TOPIC-MAP 已記，clean-code smell 表加「重複條件分支」列互接 behavioral-selection）；②「Unity 服務定位」落 unity-runtime＝unity-scripting description 列舉缺漏，補「服務定位 vs singleton」後複測 3/3 落 unity-scripting。
- [ ] 各 plugin 依實戰回饋擴充 references（三 plugin 皆無既定候選，實戰需求驅動）。
- [ ] unity-runtime 若再長，考慮 sub-split。

## 相關文件（歷史紀錄，重構時不回改）

- 各 plugin 原設計 spec/plan 未遷入 monorepo；舊 repo 已刪除，僅存於本機舊資料夾（如 `../sg-game-dev-skill/docs/superpowers/`）。
