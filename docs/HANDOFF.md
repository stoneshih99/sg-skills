# 交接 / 專案狀態

> 本檔記錄 monorepo 目前進度與下一步。撰寫規範見 [CONVENTIONS.md](CONVENTIONS.md)，主題歸屬見 [TOPIC-MAP.md](TOPIC-MAP.md)。

## 專案

`sg-skills`：Stone 的個人 Agent Skills marketplace，一個 repo 收三個正交 plugin。2026-07-24 由三個獨立 repo 合併而成。

| Plugin | 版本 | 結構 | 定位 |
|--------|------|------|------|
| **sg-game-dev-skills**（plugins/game-dev） | 0.21.3 | 5 hub / 80 篇 | 引擎中立遊戲（What/Why）。一人工作室的虛擬部門顧問團 |
| **sg-unity-dev-skills**（plugins/unity-dev） | 0.11.0 | 3 hub / 31 篇 | Unity 具體（How in Unity）。接住 game-dev 留白 |
| **sg-dev-skills**（plugins/dev） | 0.2.0 | 2 hub / 10 篇 | 通用工程（不限遊戲）。git / shell |

合計 10 hub、121 篇 reference。

## monorepo 合併（2026-07-24）

三個獨立 repo 合為一個 marketplace，理由：**個人自用，統一維護、防跨 plugin 重複設計**。

- 結構：`plugins/<x>/` 各是完整 plugin（自己的 plugin.json + skills/），頂層一個 `marketplace.json` 列三個 plugin（source 指向 plugins/*）。
- **關鍵技術現實**：安裝後每個 plugin 各自獨立快取，**跨 plugin 相對連結會斷**——跨 plugin 一律文字提及。monorepo 的真好處是：一份 CONVENTIONS、一張 TOPIC-MAP、一套 check-links、原子跨 plugin commit、一個 marketplace 一次加。
- 舊三 repo（github.com/stoneshih99/sg-{game-dev,unity-dev,dev}-skills）已刪除。
- 全新單一 git 歷史（未保留三 repo 舊 commit；舊 repo 刪除後歷史不再保存）。

## Router 結論（跨 plugin 觸發）

三 plugin 共存**不需額外 router 層**——Claude Code 的 skill description 觸發本身就是 router。精準靠「description 邊界切乾淨 + 重疊詞用層區隔」。headless probe 驗證：跨 plugin 邊界全對、unity 三 hub sonnet 7/7、dev git vs shell sonnet 6/6。**相似 hub 用 sonnet 探測，別用 haiku**（haiku 對相同 query 會給不一致答案，曾誤導判斷）。

## 各 plugin 狀態

**game-dev**：五分類全開張，一分類一 hub。architecture 的 system（8 篇）與 net（4 篇）為實作決策級深度。既定候選全數完成，後續依實戰回饋擴充。

**unity-dev**：三 hub——unity-scripting（script/input/asset/test/editor）、unity-runtime（physics/net/shader/anim/audio/ui，6 家族/約 490 字元，再長考慮再拆）、unity-optimization（perf/build）。

**dev**：git-workflow（六域 8 篇）、shell-scripting（safety/text，2026-07-24 加）。正交，routing 邊界最清楚。

## 待辦

- [x] 三 repo 合併為 sg-skills monorepo，連結檢查 0 斷鏈、validate 通過、實裝 sonnet probe 5/5（2026-07-24）。
- [x] 舊三 repo 已刪除（2026-07-24）。
- [ ] 各 plugin 依實戰回饋擴充 references（game-dev 無既定候選；dev 候選：通用除錯方法論、regex、CLI 工具）。
- [ ] unity-runtime 若再長，考慮 sub-split。

## 相關文件（歷史紀錄，重構時不回改）

- 各 plugin 原設計 spec/plan 留在各自 archived repo 的 `docs/superpowers/`。
