# sg-skills（monorepo）

本 repo 同時是 Claude Code 與 Codex marketplace，一個 repo 收三個正交的 plugin。三者定位、分層見 [README](README.md) 與 [docs/HANDOFF.md](docs/HANDOFF.md)。

## 結構

    plugins/sg-game-dev-skills/    sg-game-dev-skills（引擎中立遊戲，5 hub）
    plugins/sg-unity-dev-skills/   sg-unity-dev-skills（Unity 具體，3 hub）
    plugins/sg-dev-skills/         sg-dev-skills（通用工程，7 hub）
    .claude-plugin/marketplace.json   Claude Code marketplace
    .agents/plugins/marketplace.json  Codex marketplace
    docs/                            共用 CONVENTIONS / TOPIC-MAP / HANDOFF

每個 `plugins/<plugin-name>/` 是完整 plugin：自己的 `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json` 與共用 `skills/`。兩份 manifest 的 name、version、description、author 必須一致。

## 新增 / 修改 skill 時

1. **先查 [docs/TOPIC-MAP.md](docs/TOPIC-MAP.md)**——確認主題歸哪個 plugin 哪個 hub，避免跨 plugin 重複設計（monorepo 的核心價值）。
2. 遵循 [docs/CONVENTIONS.md](docs/CONVENTIONS.md)，特別是「單一入口（hub）模式」。
3. **新主題 = 加 reference + hub 細表加一行**；不開新 skill（除非全新分類/域）。只有出現「新的域」才動 hub description。
4. 深度標竿：實作決策級——「A 模式 vs B 模式、為什麼、何時選哪個 + 坑」，不是原則概述、不是工具教學。
5. 內文繁體中文；game-dev 偽代碼引擎中立、unity 用實際 C#、dev 用實際 shell。
6. cross-link：**同 plugin 內**用相對路徑（reference 到同 plugin 其他 hub 是 `../../<hub>/references/<file>.md`）；**跨 plugin** 一律文字提及，不用相對路徑（安裝後各 plugin 獨立快取，跨 plugin 相對連結會斷）。

## 改動後必跑的驗證

1. `python3 scripts/check-links.py`——全 monorepo 連結檢查（裸檔名 + 相對路徑 + 跨 plugin 警告）。
2. `python3 scripts/check-plugin-compat.py`——驗證雙 marketplace、雙 manifest 與扁平 skill 結構。
3. frontmatter description ≤ 1536、hub description ≤ ~400 字元。
4. `claude plugin validate .`（在 repo 根，驗 marketplace 與三個 plugin source）。

**第 1、2、4 項已由 pre-commit hook 自動化**（`scripts/hooks/pre-commit`，失敗就擋下 commit）。**重 clone 後跑一次掛上**：`git config core.hooksPath scripts/hooks`。要略過檢查用 `git commit --no-verify`。

## 發佈流程（重要）

本機安裝走版本快取，兩個平台的 plugin manifest 必須保持相同 version；內容改了但版本沒 bump，使用者可能仍拿到舊快取。

流程：改 `plugins/<plugin-name>/` 內容 → **同步 bump 該 plugin 的 Claude/Codex manifest version**（新 reference 升 minor）→ commit → push。Claude Code 執行 `claude plugin update <plugin>@sg-skills`；Codex 執行 `codex plugin marketplace upgrade sg-skills` 後再執行 `codex plugin add <plugin>@sg-skills`，並開新 task 載入新版 skill。只 bump 動到的那個 plugin。

## 其他

- Push 用 HTTPS + gh credential helper，active 帳號須為 `stoneshih99`（SSH 會認到無寫入權的 stone1001f）。
- 前身是三個獨立 repo（sg-game-dev-skills / sg-unity-dev-skills / sg-dev-skills），2026-07-24 合併為本 monorepo，舊三 repo 已刪除。
