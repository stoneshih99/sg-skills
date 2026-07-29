# Three-Layer UI Generation Workflow Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `sg-dev-skills` 加入三個可獨立觸發、可串接、且同時支援 Claude Code 與 Codex plugin 的 UI workflow skills。

**Architecture:** 三個直接位於 `skills/` 的 workflow skills 以文件契約交接：參考資料產生 UI spec、UI spec 驅動實作、可執行 UI 產生 QA 報告。核心流程不綁平台；Sites、瀏覽器、Playwright、現有前端 stack 或 Unity 工具只在 runtime 實際可用且符合任務時選用。

**Tech Stack:** Agent Skills `SKILL.md`、Markdown templates、Codex `agents/openai.yaml`、Claude/Codex plugin JSON manifests、Python repository validators、Claude plugin validator。

## Global Constraints

- 三個 skills 必須放在 `plugins/sg-dev-skills/skills/`，且各自直接包含 `SKILL.md`。
- Skill 與模板內文使用繁體中文；skill 名稱與路徑使用 kebab-case。
- canonical workflow 不寫死 Codex 或 Claude Code 專有命令。
- 跨 plugin 只用 skill/plugin 名稱文字提及，不建立相對連結。
- 使用者未要求部署時，不得把 UI 實作擴張成部署工作。
- QA 預設只診斷與報告；只有使用者同時要求修正時才改實作。
- 三個 skills 必須逐一完成 RED、GREEN、REFACTOR 與 commit，不能批次寫完才測。
- `sg-dev-skills` 版本由 `0.8.1` 提升為 `0.9.0`，Claude/Codex manifests 必須一致。

---

### Task 1: Reference to UI Spec

**Files:**
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/SKILL.md`
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-spec.md`
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/agents/openai.yaml`
- Test: fresh-agent application scenario plus `quick_validate.py`

**Interfaces:**
- Consumes: screenshot、video、URL、HTML/CSS/JS、wireframe 或文字參考，以及目標平台與原創邊界。
- Produces: 一份符合 `templates/ui-spec.md` 的 Markdown UI spec，供 Task 2 的 `build-ui-from-spec` 使用。

- [ ] **Step 1: Run the RED baseline without the new skill**

Dispatch a fresh agent without the new skill and use this exact scenario:

```text
請把這份 UI 參考描述轉成可以交給工程師實作的規格：
「桌面版深色 SaaS dashboard，左側固定導覽、上方 KPI 卡、中央折線圖、
右側活動串流；卡片 hover 上浮，載入時有 skeleton。手機版沒有參考圖。」
不要寫程式碼。
```

Score the output against these required fields:

```text
reference boundary
observations vs assumptions
goal and audience
layout and hierarchy
type and color system
assets and content
component states
motion
responsive behavior
accessibility
performance
acceptance checks
```

Expected RED: at least one of `reference boundary`、`observations vs assumptions`、mobile assumptions、reduced-motion/accessibility 或 acceptance checks is absent or merged into vague prose. Record the missing fields in the task notes before creating files.

- [ ] **Step 2: Initialize the skill**

Read `${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/references/openai_yaml.md`, then run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
  reference-to-ui-spec \
  --path plugins/sg-dev-skills/skills \
  --interface display_name="Reference to UI Spec" \
  --interface short_description="把截圖、影片或網站參考轉成可驗收且可交付的完整 UI 規格" \
  --interface default_prompt="請分析我提供的 UI 參考，建立一份可交給實作者的 UI 規格。"
```

Use `apply_patch` to create `templates/ui-spec.md`; do not retain unused generated files.

- [ ] **Step 3: Write the minimal skill**

Replace the generated `SKILL.md` with these exact frontmatter values:

```yaml
---
name: reference-to-ui-spec
description: Use when 使用者提供截圖、影片、網站、HTML、wireframe 或模糊視覺方向，希望分析、重製、借用視覺語法，或先整理成可交付工程實作的 UI 規格
---
```

The body must contain, in this order:

1. 定位：只把 reference 編譯成 spec，不實作 UI。
2. 輸入確認：可存取參考、目標使用者／平台、原創邊界。
3. 證據優先規則：原始 HTML 行為優先；影片取狀態關鍵畫面；靜態圖不可推斷精確動畫技術。
4. 分析層：觀察與假設分離。
5. UI spec workflow：goal → layout → type/color → assets/content → states → motion → responsive → accessibility/performance → acceptance。
6. 停止條件：參考不可存取或存在會改變整體方向的矛盾時，提出一個阻斷問題。
7. 輸出：複製 `templates/ui-spec.md` 的欄位；不夾帶實作或部署。
8. 常見錯誤：只描述風格、把猜測寫成事實、漏手機／狀態、抄品牌內容。

- [ ] **Step 4: Create the output template**

Create `templates/ui-spec.md` with these headings:

```markdown
# UI Spec: <名稱>

## Reference Boundary
## Goal And Audience
## Evidence
### Observations
### Assumptions
## Information Architecture
## Layout And Hierarchy
## Type And Color System
## Components And Content
## Assets
## State Matrix
## Motion
## Responsive Behavior
## Accessibility
## Performance
## Anti-Patterns
## Acceptance Checks
## Open Inputs
```

Under each heading, include one concise Traditional Chinese instruction stating what concrete evidence or decision belongs there. `Open Inputs` must say that empty means no blocking input remains.

- [ ] **Step 5: Run GREEN and REFACTOR forward tests**

Dispatch a fresh agent with:

```text
Use $reference-to-ui-spec at
plugins/sg-dev-skills/skills/reference-to-ui-spec
to solve this request:

請把這份 UI 參考描述轉成可以交給工程師實作的規格：
「桌面版深色 SaaS dashboard，左側固定導覽、上方 KPI 卡、中央折線圖、
右側活動串流；卡片 hover 上浮，載入時有 skeleton。手機版沒有參考圖。」
不要寫程式碼。
```

Expected GREEN: all twelve RED rubric fields are explicit, mobile behavior is labeled as an assumption, and no implementation/deployment is performed. If the agent still omits a field, add only the minimum structural instruction that closes that observed gap and rerun once.

- [ ] **Step 6: Validate and commit**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/reference-to-ui-spec
python3 scripts/check-links.py
git diff --check
```

Expected: all commands pass.

Commit:

```bash
git add plugins/sg-dev-skills/skills/reference-to-ui-spec
git commit -m "feat: 新增 UI 參考轉規格 workflow"
```

---

### Task 2: Build UI from Spec

**Files:**
- Create: `plugins/sg-dev-skills/skills/build-ui-from-spec/SKILL.md`
- Create: `plugins/sg-dev-skills/skills/build-ui-from-spec/templates/ui-build-brief.md`
- Create: `plugins/sg-dev-skills/skills/build-ui-from-spec/agents/openai.yaml`
- Test: fresh-agent application scenario plus `quick_validate.py`

**Interfaces:**
- Consumes: Task 1 的 UI spec，或具有相同必要欄位的既有 design brief；另外讀取目標 repository 與既有 stack。
- Produces: 可執行 UI、必要資產、最小驗證證據，以及一份固定實作邊界的 build brief。

- [ ] **Step 1: Run the RED baseline without the new skill**

Dispatch a fresh agent without the new skill:

```text
你要依照一份完整 UI spec 在既有專案實作 dashboard。專案已經有 design
tokens 和 Card 元件。請先說明你會如何執行；不要假設可以部署，也不要改檔。
```

Score these behaviors:

```text
reads project instructions and existing design system first
defines implementation boundary
reuses existing components
maps every required state
selects tools from actual runtime
does not assume deployment
defines responsive/accessibility/reduced-motion checks
separates verified and unverified results
```

Expected RED: at least one boundary, state mapping, reduced-motion check, runtime capability check, or verification-status field is absent.

- [ ] **Step 2: Initialize the skill**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
  build-ui-from-spec \
  --path plugins/sg-dev-skills/skills \
  --interface display_name="Build UI from Spec" \
  --interface short_description="依 UI 規格與現有技術棧建立可執行且可驗證的完整介面" \
  --interface default_prompt="請依照這份 UI 規格，在目前專案建立並驗證介面。"
```

Use `apply_patch` to create `templates/ui-build-brief.md`; remove no files other than unused generated placeholders.

- [ ] **Step 3: Write the minimal skill**

Use:

```yaml
---
name: build-ui-from-spec
description: Use when 使用者已有 UI spec、wireframe、設計 brief 或明確頁面需求，要求在 HTML、React、其他前端技術棧或 Unity UI 建立、修改或完成可執行介面
---
```

The body must contain:

1. 定位：實作 spec，不重新發明設計方向；缺 spec 時先建立最小 brief 或使用 `reference-to-ui-spec`。
2. 專案先行：讀 instructions、design tokens、現有 components、scripts、tests。
3. Build brief：鎖定 route/screen、stack、reuse、內容、states、交付與 non-goals。
4. 工具選擇：依當前 runtime；網站可用 Sites、既有前端 stack 或瀏覽器；Unity 轉交 Unity 專屬知識。
5. 實作順序：結構與資料 → responsive → states/interactions → motion → polish。
6. 驗證：啟動、console、viewport、keyboard/focus、loading/empty/error、reduced motion。
7. 交付：列出改動、驗證與未驗證項；只有使用者要求才部署。
8. 常見錯誤：忽略既有系統、只畫 happy path、靜態截圖冒充完成、擅自換 stack／部署。

- [ ] **Step 4: Create the build brief template**

Create `templates/ui-build-brief.md` with:

```markdown
# UI Build Brief: <名稱>

## Source Spec
## Target Repository And Route
## Existing Stack And Instructions
## Reuse Inventory
## Content And Data
## Component And State Map
## Responsive Requirements
## Accessibility And Reduced Motion
## Delivery Form
## Non-Goals
## Verification Commands
## Completion Evidence
## Unverified Items
```

Each heading gets one concrete Traditional Chinese instruction. `Completion Evidence` distinguishes commands/screenshots actually checked; `Unverified Items` must never be silently omitted.

- [ ] **Step 5: Run GREEN and REFACTOR forward tests**

Run the same RED scenario with:

```text
Use $build-ui-from-spec at
plugins/sg-dev-skills/skills/build-ui-from-spec
to solve the request.
```

Expected GREEN: all eight rubric behaviors appear, project reuse precedes new component creation, and deployment is not assumed. Patch only observed gaps and rerun.

- [ ] **Step 6: Validate and commit**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/build-ui-from-spec
python3 scripts/check-links.py
git diff --check
```

Commit:

```bash
git add plugins/sg-dev-skills/skills/build-ui-from-spec
git commit -m "feat: 新增 UI 規格實作 workflow"
```

---

### Task 3: Visual UI QA

**Files:**
- Create: `plugins/sg-dev-skills/skills/visual-ui-qa/SKILL.md`
- Create: `plugins/sg-dev-skills/skills/visual-ui-qa/templates/ui-qa-report.md`
- Create: `plugins/sg-dev-skills/skills/visual-ui-qa/agents/openai.yaml`
- Test: fresh-agent application scenario plus `quick_validate.py`

**Interfaces:**
- Consumes: 可執行 UI/build、Task 1 UI spec 或其他驗收基準、viewport 與互動路徑。
- Produces: 按嚴重度排序、附重現條件與證據的 UI QA report；預設不修改實作。

- [ ] **Step 1: Run the RED baseline without the new skill**

Dispatch a fresh agent without the skill:

```text
一個 dashboard 在桌面看起來正常，但手機有人回報橫向捲動，鍵盤使用者也不確定
焦點在哪。請說明你會怎麼驗收並回報；目前只診斷，不要修。
```

Score:

```text
load/console gate
explicit viewports
reproducible interaction path
layout/overflow evidence
keyboard/focus
loading/empty/error states
reduced motion
spec mismatch vs defect vs missing evidence vs preference
severity and minimal fix direction
diagnose-only boundary
```

Expected RED: at least one evidence category、分類、state、reduced-motion 或 diagnose-only boundary is missing.

- [ ] **Step 2: Initialize the skill**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
  visual-ui-qa \
  --path plugins/sg-dev-skills/skills \
  --interface display_name="Visual UI QA" \
  --interface short_description="以可重現證據驗收 UI 視覺、響應式、可及性與互動狀態" \
  --interface default_prompt="請依規格驗收這個 UI，產生附證據且按嚴重度排序的報告。"
```

Use `apply_patch` to create `templates/ui-qa-report.md`; remove no files other than unused generated placeholders.

- [ ] **Step 3: Write the minimal skill**

Use:

```yaml
---
name: visual-ui-qa
description: Use when 已完成或可執行的 UI 需要規格比對、視覺驗收、響應式檢查、可及性檢查，或正在調查跑版、overflow、focus、互動狀態與視覺回歸問題
---
```

The body must contain:

1. 定位：先產生可重現診斷；未要求修正時不改實作。
2. 基準確認：spec、參考圖、viewport、互動路徑與可接受差異。
3. 啟動 gate：頁面可載入、console 無阻斷錯誤。
4. 證據矩陣：viewport × state × interaction。
5. 檢查面：layout/overflow、type/color/assets、keyboard/focus、loading/empty/error、motion/reduced motion。
6. 分類：規格不符、實作缺陷、參考不足、主觀偏好。
7. 報告：severity、重現、預期、實際、證據、最小修正方向。
8. 停止條件與誠實邊界：環境起不來或參考不足時，不宣稱已完成。

- [ ] **Step 4: Create the QA report template**

Create `templates/ui-qa-report.md`:

```markdown
# UI QA Report: <名稱>

## Scope And Baseline
## Environment
## Evidence Matrix
## Findings
### <Severity> — <問題>
- Classification:
- Reproduction:
- Expected:
- Actual:
- Evidence:
- Minimal Fix Direction:
## Passed Checks
## Missing Evidence
## Verification Boundary
```

Add concise instructions defining severity as blocker/high/medium/low and requiring every finding to cite captured or observed evidence.

- [ ] **Step 5: Run GREEN and REFACTOR forward tests**

Run the RED scenario with:

```text
Use $visual-ui-qa at
plugins/sg-dev-skills/skills/visual-ui-qa
to solve the request.
```

Expected GREEN: all ten rubric behaviors are present, findings are evidence-backed, and no fix is performed. Patch observed gaps only and rerun.

- [ ] **Step 6: Validate and commit**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/visual-ui-qa
python3 scripts/check-links.py
git diff --check
```

Commit:

```bash
git add plugins/sg-dev-skills/skills/visual-ui-qa
git commit -m "feat: 新增視覺 UI QA workflow"
```

---

### Task 4: Dual-Plugin Routing and Release Metadata

**Files:**
- Modify: `plugins/sg-dev-skills/.claude-plugin/plugin.json`
- Modify: `plugins/sg-dev-skills/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `docs/TOPIC-MAP.md`
- Modify: `docs/CONVENTIONS.md`

**Interfaces:**
- Consumes: the three verified skill directories from Tasks 1–3.
- Produces: Claude exact skill list、Codex directory discovery、`0.9.0` synchronized metadata and user-facing routing.

- [ ] **Step 1: Run the compatibility check to verify RED**

Run:

```bash
python3 scripts/check-plugin-compat.py
```

Expected: FAIL because Claude manifest does not yet list the three direct skill directories.

- [ ] **Step 2: Update both plugin manifests**

In both manifests:

- Set `"version": "0.9.0"`.
- Extend description with `UI 參考轉規格、依規格實作、視覺 QA` without removing existing domains.

In Claude `skills`, append:

```json
"./skills/reference-to-ui-spec",
"./skills/build-ui-from-spec",
"./skills/visual-ui-qa"
```

In Codex interface:

- Keep `"skills": "./skills"`.
- Extend `shortDescription` and `longDescription` with UI workflow coverage.
- Keep existing category, author and capability values.

- [ ] **Step 3: Update routing documentation**

Apply these exact ownership rules:

- `docs/TOPIC-MAP.md`: add all three workflow names to `sg-dev-skills`; add a UI generation boundary row distinguishing generic workflow, game UI/UX decisions, and Unity UI implementation.
- `docs/CONVENTIONS.md`: document that up to three clearly separated executable workflows may remain standalone; knowledge collections still use hubs, and four or more overlapping workflows trigger a hub review.
- `README.md`: update `sg-dev-skills` content and count from 7 to 10 skills; add a short three-stage UI workflow example.
- `.claude-plugin/marketplace.json`: extend only `sg-dev-skills` marketplace description.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
git diff --check
```

Expected: all pass, with link count `>=696`; zero broken links and cross-plugin warnings are the primary conditions, and all three plugins are reported compatible.

- [ ] **Step 5: Commit**

```bash
git add \
  plugins/sg-dev-skills/.claude-plugin/plugin.json \
  plugins/sg-dev-skills/.codex-plugin/plugin.json \
  .claude-plugin/marketplace.json \
  README.md \
  docs/TOPIC-MAP.md \
  docs/CONVENTIONS.md
git commit -m "docs: 發佈三層 UI workflow skills"
```

---

### Task 5: Full Regression and Local Install Smoke

**Files:**
- Verify only; modify Task 1–4 files only if a test exposes a defect.

**Interfaces:**
- Consumes: released `sg-dev-skills@0.9.0`.
- Produces: evidence that repository structure and local plugin installation expose all three skills.

- [ ] **Step 1: Run repository regression**

```bash
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
git diff --check
git status --short --branch
```

Expected: all validators pass; the approved worktree is clean and, relative to `origin/main`, behind is 0 while ahead includes the feature commits.

- [ ] **Step 2: Run an isolated Codex local-install smoke**

Create an isolated temporary Codex home, add the repository marketplace, install `sg-dev-skills`, and list installed files using the currently available Codex plugin CLI syntax. Verify these exact installed paths exist:

```text
skills/reference-to-ui-spec/SKILL.md
skills/build-ui-from-spec/SKILL.md
skills/visual-ui-qa/SKILL.md
```

Do not alter the user's normal Codex home.

- [ ] **Step 3: Run a Claude discovery smoke**

Use `claude plugin validate .` output plus the Claude manifest list to verify all ten `sg-dev-skills` entries are discoverable. Do not install into the user's global Claude environment.

- [ ] **Step 4: Final review**

Inspect:

```bash
git log --oneline -8
git status --short --branch
```

Confirm:

- one design commit
- one plan commit
- one commit per new skill
- one release/routing commit
- no unrelated files
- no push unless the user separately requests it
