# 交接 / 專案狀態

> 本檔記錄 monorepo 目前進度與下一步。撰寫規範見 [CONVENTIONS.md](CONVENTIONS.md)，主題歸屬見 [TOPIC-MAP.md](TOPIC-MAP.md)。

## 專案

`sg-skills`：Stone 的個人 Agent Skills marketplace，同時支援 Claude Code 與 Codex；一個 repo 收三個正交 plugin。2026-07-24 由三個獨立 repo 合併而成。

| Plugin | 版本 | 結構 | 定位 |
|--------|------|------|------|
| **sg-game-dev-skills**（plugins/sg-game-dev-skills） | 0.27.0 | 5 hub + 1 workflow / 90 篇 reference | 引擎中立遊戲（What/Why）。一人工作室的虛擬部門顧問團 |
| **sg-unity-dev-skills**（plugins/sg-unity-dev-skills） | 0.16.3 | 3 hub / 36 篇 | Unity 具體（How in Unity）。接住 game-dev 留白 |
| **sg-dev-skills**（plugins/sg-dev-skills） | 0.10.0 | 10 skills / 26 篇 | 通用工程，加上 UI 證據／規格／設計系統、實作與視覺回歸 workflow |

合計 19 skills、152 篇 reference。

## monorepo 合併（2026-07-24）

三個獨立 repo 合為一個 marketplace，理由：**個人自用，統一維護、防跨 plugin 重複設計**。

- 結構：`plugins/<plugin-name>/` 各是完整 plugin（Claude/Codex manifest + 共用 skills/），兩套 marketplace 都列相同三個 plugin。
- **關鍵技術現實**：安裝後每個 plugin 各自獨立快取，**跨 plugin 相對連結會斷**——跨 plugin 一律文字提及。monorepo 的真好處是：一份 CONVENTIONS、一張 TOPIC-MAP、一套 check-links、原子跨 plugin commit、一個 marketplace 一次加。
- 舊三 repo（github.com/stoneshih99/sg-{game-dev,unity-dev,dev}-skills）已刪除。
- 全新單一 git 歷史（未保留三 repo 舊 commit；舊 repo 刪除後歷史不再保存）。

## 驗證自動化（pre-commit hook）

改動後必跑的檢查已由 pre-commit hook 強制執行（「機器可查的進 hook」）：

- **`scripts/hooks/pre-commit`**（版控追蹤）：commit 前自動跑 `check-links.py`、`check-plugin-compat.py`、`check-ui-workflows.py`、`check-game-delivery-workflow.py` 與 `claude plugin validate .`，失敗就擋下 commit。`claude` 不在 PATH 時只略過官方 Claude validate，其餘檢查照跑。
- **掛法靠 `core.hooksPath`**（非 `.git/hooks/`，故進版控、重 clone 也在）。**重 clone 後跑一次**：`git config core.hooksPath scripts/hooks`。略過檢查用 `git commit --no-verify`。
- 兩條路徑都測過：正常 commit 通過、故意斷鏈 exit 1 擋下。

## Router 結論（跨 plugin 觸發）

三 plugin 共存**不需額外 router 層**——Claude Code 的 skill description 觸發本身就是 router。精準靠「description 邊界切乾淨 + 重疊詞用層區隔」。headless probe 驗證：跨 plugin 邊界全對、unity 三 hub sonnet 7/7；dev 六 hub 每加一 hub 都實裝 probe（git vs shell 6/6、+clean-code 6/6、+debug 7/7、+regex 6/7——1 題為 TOPIC-MAP 記錄的合理軟邊界、+cli 7/7，cli↔shell 零滲漏）。**相似 hub 用 sonnet 探測，別用 haiku**（haiku 對相同 query 會給不一致答案，曾誤導判斷）。

## 各 plugin 狀態

**game-dev**：五分類全開張，一分類一 hub。architecture 的 system（8 篇）與 net（4 篇）為實作決策級深度。既定候選全數完成，後續依實戰回饋擴充。

**unity-dev**：三 hub——unity-scripting（script/input/asset/test/editor）、unity-runtime（physics/net/shader/anim/audio/ui/2d，7 家族、description 已超 ~400 字元準則，**再加家族前先拆 hub**）、unity-optimization（perf/build）。

**dev**：七個通用工程 skills 維持原有邊界；另有三個 UI workflow——`reference-to-ui-spec` 收證據捕捉、頁面規格與設計系統抽取，`build-ui-from-spec` 收依規格實作與可測狀態交接，`visual-ui-qa` 收人工診斷與自動視覺回歸。`sg-dev-skills` 合計 26 篇 references，其中三個 UI workflow 本身合計 3 篇 workflow references，後續依實戰需求擴充。

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
- [x] design-patterns 瘦身（2026-07-26）：三篇壓成單篇（砍 structural——最接近「Claude 已知」的純教學），description 328→183 字元。**判準記下來**：內容值不值得進 skill，看它是「Claude 會說錯」（版本漂移/架構誤解，最值得）、「知道但不會主動說」（平台坑/設定細節，值得），還是「知道且會說、只差預設值」（用 CLAUDE.md 一行即可，不該開 hub）。瘦身後複測：狀態機實作 3/3 design-patterns、遊戲 AI FSM 3/3 game-architecture、通用 singleton 3/3 design-patterns、Unity 服務定位 2/2 unity-scripting。
- [x] dev 新增三階段 UI workflow，並補齊 UI 證據捕捉、design system 抽取、可測實作交接與自動視覺回歸（2026-07-29）。
- [x] game-dev 新增小型完整遊戲總控 workflow，涵蓋七階段、部門交接與 Release Candidate Build（2026-07-29）。
- [ ] 各 plugin 依實戰回饋擴充 references（三 plugin 皆無既定候選，實戰需求驅動）。
- [ ] unity-runtime 若再長，考慮 sub-split。

## 相關文件（歷史紀錄，重構時不回改）

- 各 plugin 原設計 spec/plan 未遷入 monorepo；舊 repo 已刪除，僅存於本機舊資料夾（如 `../sg-game-dev-skill/docs/superpowers/`）。
