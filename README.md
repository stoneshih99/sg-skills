# sg-skills

Stone 的個人 **Agent Skills marketplace**，同時支援 Claude Code Plugin 與 Codex Plugin。一個 repo、兩套 marketplace manifest、三個正交的 plugin，各自可選裝。

| Plugin | 層 | 對應 | 內容 |
|--------|----|------|------|
| **sg-game-dev-skills** | 引擎中立遊戲（What/Why） | 一人工作室的虛擬部門顧問團 | 企畫 / 架構 / 工具 / 工作流 / 畫圖，5 hub |
| **sg-unity-dev-skills** | Unity 具體（How in Unity） | 接住 game-dev 刻意留白的引擎實作 | 腳本 / 執行期 / 優化，3 hub |
| **sg-dev-skills** | 通用工程（不限遊戲） | 跨領域決策與坑 | git / shell / Clean Code / 除錯方法論 / regex / CLI / 設計模式 / UI 證據與規格 / 設計系統 / 實作 / 視覺回歸，10 skills |

三者**分層正交**：game-dev 講「該怎麼設計、為什麼」，unity 講「在 Unity 具體怎麼做」，dev 講「跟遊戲無關的通用工程」。

## UI 三階段 workflow

1. `reference-to-ui-spec`：捕捉網站、影片或 HTML 的 UI 證據，整理 UI spec，或抽取可重用的設計系統。
2. `build-ui-from-spec`：依已確認的 UI spec 與 design system，在既有專案完成實作及可重現狀態交接。
3. `visual-ui-qa`：以 spec 與可重現證據進行人工驗收，或規劃 deterministic screenshot regression。

遊戲 UI/UX 的設計決策仍由 `sg-game-dev-skills` 處理；Unity 的 uGUI、UI Toolkit 與 API 實作仍由 `sg-unity-dev-skills` 處理。

## 為什麼需要這些 skill

**模型知道 DDD、知道所有優化手法——但寫 code 的當下，決定行為的是 context 裡有什麼，不是模型會什麼。**

沒有指引時，Agent 的預設目標是「完成這次任務」：你說「加一個技能系統」，它挑一條看起來合理的最短路徑做出來、能跑、收工。它不會主動問「這專案該領域模型還是資料驅動？第 30 個技能時這寫法撐得住嗎？」——這些不在任務描述裡，它預設不替你做超出任務的決策。每次任務都做對，30 次後卻長成不一致的系統：**每一局都贏，整場棋輸了**。

Skill 把預設值換掉——從「能跑就好」換成「照這套標準做」。觸發後不是模型變聰明了，是**你的決策先進了它的 context**。成本靠**漸進式揭露**：各 plugin 的 hub description 常駐（付「何時該載入」的判斷成本），上百篇內容觸發才進 context。

## 安裝

### Claude Code

一次加入 marketplace，再各自選裝需要的 plugin：

    claude plugin marketplace add stoneshih99/sg-skills

    # 遊戲知識——建議 project level（只在遊戲專案載入、設定跟著專案走）
    claude plugin install sg-game-dev-skills@sg-skills --scope project
    claude plugin install sg-unity-dev-skills@sg-skills --scope project

    # 通用工程——每個專案都用得到，可裝 user level
    claude plugin install sg-dev-skills@sg-skills

互動 session 內等效指令為 `/plugin marketplace add` 與 `/plugin install`。

**更新**：內容更新只在對應 plugin 的 `plugin.json` version 提升後生效——`claude plugin update <plugin>@sg-skills`。

### Codex

    codex plugin marketplace add stoneshih99/sg-skills

    codex plugin add sg-game-dev-skills@sg-skills
    codex plugin add sg-unity-dev-skills@sg-skills
    codex plugin add sg-dev-skills@sg-skills

**更新**：先刷新 marketplace，再重新安裝需要更新的 plugin：

    codex plugin marketplace upgrade sg-skills
    codex plugin add <plugin>@sg-skills

更新後開一個新的 Codex task，讓新版 skill 進入新的 context。

> **注意**：`@sg-skills` 是 **marketplace 名**（本 repo），不是 plugin 名——兩個平台的三個 plugin 都從這個 marketplace 安裝。

## 結構

    sg-skills/
    ├── .claude-plugin/marketplace.json   # Claude Code marketplace
    ├── .agents/plugins/marketplace.json  # Codex marketplace
    ├── plugins/
    │   ├── sg-game-dev-skills/    (.claude-plugin/ + .codex-plugin/ + skills/)
    │   ├── sg-unity-dev-skills/
    │   └── sg-dev-skills/
    ├── docs/
    │   ├── CONVENTIONS.md   # 三 plugin 共用的撰寫規範
    │   ├── TOPIC-MAP.md     # 主題歸屬總表（防重複設計）
    │   └── HANDOFF.md       # 交接 / 專案狀態
    └── scripts/
        ├── check-links.py          # 全 monorepo 連結檢查
        ├── check-plugin-compat.py  # 雙平台結構與 metadata 檢查
        ├── check-ui-workflows.py   # UI workflow 能力、資源與版本契約
        └── hooks/pre-commit        # commit 前自動驗證

## 新增 / 修改 skill

撰寫規範見 [docs/CONVENTIONS.md](docs/CONVENTIONS.md)；寫新內容前先查 [docs/TOPIC-MAP.md](docs/TOPIC-MAP.md) 確認歸屬、避免跨 plugin 重複。

## 驗證（pre-commit hook）

commit 前自動跑連結檢查、雙平台相容檢查、UI workflow 契約與 `claude plugin validate`，失敗就擋下。**clone 後跑一次掛上**：

    git config core.hooksPath scripts/hooks

（`core.hooksPath` 是本機設定、不隨 commit 走，故重 clone 需重掛；略過檢查用 `git commit --no-verify`。）
