# UI 證據、設計系統與視覺回歸能力設計

## 目標

在不增加頂層 UI workflow skill 數量的前提下，補齊三項能力：

1. 從網站、影片、HTML 或本機畫面取得可追溯的 UI 證據。
2. 從參考或既有產品抽取可重用的設計系統。
3. 將人工視覺 QA 轉成可重跑的自動視覺回歸計畫。

完成後仍維持既有三個入口：

```text
reference-to-ui-spec
  ├─ 捕捉 UI 證據
  ├─ 產生頁面 UI spec
  └─ 抽取設計系統

build-ui-from-spec
  └─ 依 spec、design system 與可測狀態實作

visual-ui-qa
  ├─ 人工視覺診斷
  └─ 自動視覺回歸
```

## 結構裁決

### 採用：擴充現有三個 workflow

- `reference-to-ui-spec` 增加「證據捕捉」與「設計系統抽取」兩種輸出模式。
- `build-ui-from-spec` 增加 design system 消費契約與 deterministic test state 要求。
- `visual-ui-qa` 增加「自動視覺回歸」輸出模式。

理由：

- `docs/CONVENTIONS.md` 規定最多三個邊界清楚的獨立 workflow；現有 UI workflow 已達三個。
- 三項新能力分別是既有參考、實作與 QA 階段的子流程，不需要新的頂層觸發入口。
- 保留已發佈的 skill 名稱，避免 Claude Code、Codex manifest、README 與使用者提示一起改名。

### 不採用：新增三個頂層 skills

會形成六條高度相關的 description，增加觸發重疊，也直接違反目前 workflow 數量規範。

### 不採用：重構成兩個大型 hub

雖可降低入口數量，但會破壞剛建立的三層名稱與交接契約；本次沒有足夠收益支持改名與遷移成本。

## 能力一：捕捉 UI 證據

### 觸發與路由

當使用者要求擷取、記錄或分析網站、影片、HTML、畫面狀態、scroll 行為或完整頁面時，`reference-to-ui-spec` 進入 evidence capture 模式。若使用者只要求 spec，可先使用現有證據；證據不足時才執行捕捉。

### 輸入

- 可存取的網站 URL、影片、本機 HTML、應用畫面或圖片。
- 目標 viewport、狀態、互動路徑與權利邊界。
- 當前 runtime 實際可用的瀏覽器、媒體或檔案工具。

### 工作流程

1. 先記錄來源、取得時間、viewport 與可觀察範圍。
2. 網站優先保留完整頁面，再由同一來源切出連續 section crops。
3. 影片先取得 duration、dimensions、frame rate 等技術資料，再依互動節點抽取代表影格；不可用固定間隔影格冒充所有重要狀態。
4. HTML/CSS/JS 可存取時，以原始結構與行為作為技術證據；截圖只能證實可見結果。
5. 記錄 default、hover、focus、active、loading、empty、error、success、responsive 與 motion 中實際取得的狀態。
6. 缺少或無法取得的證據明列在缺口，不用推測補齊。

### 輸出

新增 `templates/ui-evidence-manifest.md`，至少包含：

- source 與 rights boundary
- capture environment
- full-page／viewport／section evidence
- motion frames 與時間點
- interaction／state matrix
- asset provenance
- observations、assumptions 與 missing evidence

不新增固定工具腳本。瀏覽器、`ffprobe`、`ffmpeg` 或專案測試工具只能在當前環境已提供且適合來源時選用。

## 能力二：抽取 UI Design System

### 觸發與路由

當使用者要求從參考、既有 UI、HTML/CSS、元件庫或多個頁面整理 design tokens、component inventory、variants 或設計語言時，`reference-to-ui-spec` 進入 design-system extraction 模式。

### 工作流程

1. 先界定來源範圍與證據可信度；程式碼 tokens 優先於截圖估值。
2. 分離 primitive、semantic 與 component tokens，不把每個原始值都變成 token。
3. 盤點 component、variant、state、responsive behavior 與 content rule。
4. 區分可重用 pattern 與 one-off composition。
5. 找出同義 token、近似值、命名衝突與缺少狀態，但不在未授權時直接重寫產品程式碼。
6. 對無法由來源證明的值標示 inferred 或 proposed。

### 輸出

新增 `templates/ui-design-system.md`，至少包含：

- design principles
- source/evidence boundary
- primitive 與 semantic tokens
- typography、spacing、radius、elevation、motion tokens
- component inventory
- variants 與 state contracts
- responsive patterns
- asset/icon rules
- reuse map、one-off list 與 unresolved decisions

輸出是語意化設計系統規格，不限定一定產生特定格式的 `tokens.json`。只有目標專案已採用明確 token schema 時，才依該 schema 另外輸出機器可讀檔案。

## 能力三：自動視覺回歸

### 觸發與路由

當使用者要求 screenshot baseline、pixel diff、Playwright visual tests、CI 視覺檢查或可重跑的 UI regression suite 時，`visual-ui-qa` 進入 automated regression 模式。一般「幫我看畫面是否跑版」仍走既有人工診斷模式。

### 工作流程

1. 確認專案現有 test runner、瀏覽器能力與 baseline 儲存慣例；不擅自更換技術棧。
2. 建立 `viewport × theme × state × interaction` 的最小風險矩陣。
3. 固定資料、時間、locale、timezone、字型、動畫與網路結果；無法固定的區域才使用窄範圍 mask。
4. baseline 必須由已確認的正確畫面產生，不以首次測試輸出自動視為正確。
5. 將 layout regression、content drift、rendering noise 與 intentionally changed baseline 分開。
6. CI 失敗時保留 expected、actual、diff 與重現命令。
7. baseline 更新必須是顯式操作，並附變更理由；不得為了讓 CI 通過自動接受差異。

### 輸出

新增 `templates/ui-regression-plan.md`，至少包含：

- runner 與啟動命令
- deterministic environment
- coverage matrix
- baseline ownership 與 review policy
- threshold／mask rules
- artifact paths
- local／CI commands
- baseline update procedure
- known nondeterminism 與 verification boundary

skill 提供測試設計與驗證契約；實際 test files、設定與 CI 修改只在使用者要求實作自動測試時進入目標專案。

## `build-ui-from-spec` 交接補強

`build-ui-from-spec` 不新增輸出模式，只增加兩項輸入要求：

1. 若有 `ui-design-system.md` 或專案既有 tokens/components，先建立 reuse map，再新增 UI。
2. 對需要自動回歸的 state 提供可重現觸發方式；優先使用專案既有 fixture、Storybook、test route 或 mock 機制，不為單次畫面另建抽象框架。

交付時列出哪些 viewport、state、theme 與互動可被測試穩定重現。

## 檔案設計

### 新增

- `scripts/check-ui-workflows.py`
- `plugins/sg-dev-skills/skills/reference-to-ui-spec/references/capture-ui-evidence.md`
- `plugins/sg-dev-skills/skills/reference-to-ui-spec/references/extract-ui-design-system.md`
- `plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-evidence-manifest.md`
- `plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-design-system.md`
- `plugins/sg-dev-skills/skills/visual-ui-qa/references/automated-visual-regression.md`
- `plugins/sg-dev-skills/skills/visual-ui-qa/templates/ui-regression-plan.md`

### 修改

- `plugins/sg-dev-skills/skills/reference-to-ui-spec/SKILL.md`
- `plugins/sg-dev-skills/skills/reference-to-ui-spec/agents/openai.yaml`
- `plugins/sg-dev-skills/skills/build-ui-from-spec/SKILL.md`
- `plugins/sg-dev-skills/skills/build-ui-from-spec/agents/openai.yaml`
- `plugins/sg-dev-skills/skills/visual-ui-qa/SKILL.md`
- `plugins/sg-dev-skills/skills/visual-ui-qa/agents/openai.yaml`
- `plugins/sg-dev-skills/.claude-plugin/plugin.json`
- `plugins/sg-dev-skills/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `README.md`
- `docs/CONVENTIONS.md`
- `docs/HANDOFF.md`
- `docs/TOPIC-MAP.md`
- `scripts/hooks/pre-commit`

不新增 README、安裝指南、變更日誌或綁定單一框架的 starter。

## Plugin 與版本策略

- 三個 canonical skills 仍由 Claude Code 與 Codex 共用，不建立平台副本。
- Claude manifest 的 skills 路徑不增加；Codex manifest 仍指向 `./skills`。
- `sg-dev-skills` 由 `0.9.0` 提升為 `0.10.0`，兩份 plugin manifest 同步。
- Claude marketplace 更新使用者可見描述；Codex marketplace 沒有版本或描述欄位，維持既有 source、policy 與 category。
- `agents/openai.yaml` 只更新既有 display、short description 或 default prompt，使新能力可被發現；不加入未要求的可選欄位。
- 文件與範本全部使用相對連結，不寫 repository 絕對路徑。

## 測試策略

### RED

先建立 `scripts/check-ui-workflows.py`，加入 pre-commit hook，並確認它在實作前因下列契約缺口失敗：

- 三個新模板不存在時失敗。
- `reference-to-ui-spec` 未路由 evidence capture／design system extraction 時失敗。
- `build-ui-from-spec` 未要求 deterministic states 時失敗。
- `visual-ui-qa` 未路由 automated regression 時失敗。
- manifest 版本未同步為 `0.10.0` 時失敗。

### GREEN

逐項加入最小文件與路由，使契約檢查通過。每完成一項能力，執行對應 skill 的 `quick_validate.py`，不等三項全部寫完才驗證。

### 完整驗證

```bash
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
```

另外驗證：

- `reference-to-ui-spec`、`build-ui-from-spec`、`visual-ui-qa` 各自通過 `quick_validate.py`。
- Claude manifest 仍只有原本 10 個 skill entries，新增能力不製造第四個 UI workflow。
- Codex 隔離安裝可發現三個既有 UI skills 與新增 bundled resources。
- description 保持在專案長度限制內，且三者觸發邊界沒有互相吞掉。
- repository 追蹤內容沒有本機絕對路徑。
- worktree 最終乾淨，feature branch 相對 `origin/main` 應為 behind 0 並包含本次 PR commits；不要求 ahead 為 0。

## 成功標準

- 使用者要求「幫我完整捕捉這個頁面／影片的 UI 證據」時，Agent 透過 `reference-to-ui-spec` 產生完整 evidence manifest，不把猜測寫成觀察。
- 使用者要求「從這些畫面或元件抽出 design system」時，同一 skill 產生語意 tokens、component inventory 與不確定性邊界。
- 使用者要求「替這個 UI 建立 screenshot regression」時，`visual-ui-qa` 產生可落地的 deterministic regression plan，並在目標專案授權範圍內實作測試。
- `build-ui-from-spec` 能消費設計系統並交付可穩定觸發的 UI states。
- 三個頂層 UI workflow 名稱維持不變，Claude Code 與 Codex plugin 都能安裝。
- repository validators 與 skill validators 全部通過。
