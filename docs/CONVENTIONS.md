# Skill 撰寫規範（三 plugin 共用）

本 monorepo 三個 plugin（sg-game-dev-skills / sg-unity-dev-skills / sg-dev-skills）共用同一套 hub playbook。差異只在題材與偽代碼語言，結構與紀律一致。

## 定位（收什麼、不收什麼）

- **收**：「A 模式 vs B 模式、為什麼、何時選哪個」的**實作決策級**知識，加上踩過的坑、慣例、驗收標準。
- **不收**：工具/API 基礎教學（Claude 已知）；個人硬規則（如 commit message 格式、C# 命名——留使用者 CLAUDE.md，plugin 要能分享，不假設讀者的 CLAUDE.md）。
- 三 plugin 的分工邊界見 [TOPIC-MAP.md](TOPIC-MAP.md)——**寫新內容前必查**，避免跨 plugin 重複設計。

## 目錄與分類

- 每個 plugin 在 `plugins/<plugin-name>/`，內含 `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json` 與共用 `skills/`。
- Skill hub 直接放在 `skills/<hub>/`；Claude manifest 明列各 hub，Codex manifest 指向整個 `./skills`。
- 新增 hub：建立 `skills/<hub>/`，並在 Claude manifest 的 `skills` 陣列加一行；Codex manifest 不需改路徑。

## 單一入口模式（hub skill）

同一領域主題超過 3-4 個時，**合併成一個 hub skill**，避免多條相近 description 觸發重疊：

- 一條 description 涵蓋全域觸發情境；路由靠 SKILL.md 內「域總表 → 各域細表（何時 / 讀哪篇）」，不靠模型從多條相近描述猜。
- references 攤平同一層，用**家族前綴**分域（`perf-*`、`net-*`、`branch-*`…）。
- SKILL.md 開頭加**定位聲明**（知識入口或可執行工作流、與其他 hub 的搭配）。
- 新增主題 = 加 reference + 細表加一行；只有出現「新的域」才擴 description。

### 可執行 workflow 的例外

最多三個邊界清楚、可各自執行的 workflow 可維持獨立 skill；知識集合仍使用 hub。當出現四個以上彼此重疊的 workflow 時，必須重新檢視是否合併為 hub。

同一階段的子流程優先放在既有 workflow 的 `references/` 與 `templates/`，由 `SKILL.md` 模式路由。例如 UI 證據捕捉、設計系統抽取與自動視覺回歸分別屬於現有參考／QA 階段，不另增入口。

總控 workflow 只負責階段、範圍、交接、核准與證據；不得複製既有專業 hub 的內容，專業決策應路由回原 hub。

### hub description 的撰寫原則

description 是**使用者會說出口的話**，不是目錄——「讀哪一篇」由路由表負責，description 只需讓模型決定「要不要開這個 hub」。

- **只寫一次**：別「涵蓋 X」又「當要做 X 時使用」講兩遍。
- **保留使用者用語**（ECS、rollback、rebase、reflog、「效能太差」「檔名有空格就爆」），**刪掉內部術語**（JPS、spatial hash、AOI 這類只在 reference 內文出現的詞）。
- **長度上限 ~400 字元**：超過代表在窮舉目錄。全 repo description 總和是每個 session 的常駐成本，當預算管。

## SKILL.md 與 references

- **SKILL.md 輕薄**：frontmatter `description`（繁中、做什麼+何時用、≤1536 字元）+ 域總表 + 家族細表。細節一律下放 references。
- **references 漸進式揭露**：一檔一主題，檔名 kebab-case 語意化並帶家族前綴。
- **reference 組織**：「決策/何時用 → 選型對照（A vs B）→ 偽代碼/指令範例 → 坑」，末附速查。
- **範例語言**：game-dev 偽代碼引擎中立、unity 用實際 C#；dev 依 hub——git/shell/cli 用實際指令，clean-code/debug/regex 語言中立（範例可用任一常見語言，不綁定）。內文一律繁體中文。

## cross-link 規則

- **同 plugin 內**用相對路徑：reference 到同 plugin 其他 hub 是 `../../<hub>/references/<file>.md`（從 references/ 出發往上兩層到 skills/）。
- **跨 plugin**一律**文字提及**，不用相對路徑——安裝後各 plugin 獨立快取，跨 plugin 相對連結會斷。

## 改動後必跑

1. `python3 scripts/check-links.py`——全 monorepo 連結檢查。
2. `python3 scripts/check-plugin-compat.py`——雙平台 marketplace、manifest 與 skill 結構檢查。
3. `python3 scripts/check-ui-workflows.py`——UI workflow 能力、資源與版本契約。
4. `python3 scripts/check-game-delivery-workflow.py`——完整遊戲交付 workflow 契約。
5. frontmatter description ≤ 1536、hub description ≤ ~400。
6. `claude plugin validate .`

第 1、2、3、4、6 項由 **pre-commit hook 自動強制**（`scripts/hooks/pre-commit`，失敗擋下 commit）——「機器可查的進 hook」。第 5 項是人工判斷，仍需自查。重 clone 後跑一次掛上：`git config core.hooksPath scripts/hooks`；略過用 `git commit --no-verify`。

## 發佈

改 `plugins/<plugin-name>/` 內容 → 同步 bump `.claude-plugin/plugin.json` 與 `.codex-plugin/plugin.json` version → commit → push。Claude Code 用 `claude plugin update <plugin>@sg-skills`；Codex 依序執行 `codex plugin marketplace upgrade sg-skills`、`codex plugin add <plugin>@sg-skills`，再開新 task 載入新版 skill。只 bump 動到的 plugin。
