# UI Evidence, Design System, and Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 擴充既有三個 UI workflow，使其支援 UI 證據捕捉、設計系統抽取與自動視覺回歸，同時維持 Claude Code 與 Codex 雙 plugin 安裝相容。

**Architecture:** 不新增第四個 UI skill。`reference-to-ui-spec` 透過兩份漸進式 reference 與兩份模板承接捕捉／抽取；`build-ui-from-spec` 補強可重用設計系統與 deterministic state 交接；`visual-ui-qa` 透過一份 reference 與模板承接自動視覺回歸。根層驗證器以可機器檢查的檔案、路由、版本與相對路徑契約防止退化。

**Tech Stack:** Markdown Agent Skills、YAML OpenAI skill metadata、Python 3 static validator、JSON plugin manifests、Claude Code plugin validator。

## Global Constraints

- 維持 `reference-to-ui-spec`、`build-ui-from-spec`、`visual-ui-qa` 三個頂層 UI workflow，不新增第四個 skill entry。
- 三個 canonical skill 目錄同時供 Claude Code 與 Codex 使用，不建立平台副本。
- 所有 repository 文件與模板使用相對連結，不寫本機或 repository 絕對路徑。
- `sg-dev-skills` 版本由 `0.9.0` 提升為 `0.10.0`，兩份 plugin manifests 同步；Claude marketplace 只更新文字描述，Codex marketplace 維持既有 schema。
- 不加入綁定單一瀏覽器、前端框架、測試 runner 或部署平台的實作。
- 每項 skill 行為先以 failing contract check 證明缺口，再寫最小內容使其通過。

---

### Task 1: 建立 UI workflow 契約驗證器並確認 RED

**Files:**
- Create: `scripts/check-ui-workflows.py`
- Modify later: `scripts/hooks/pre-commit`

**Interfaces:**
- Consumes: repository root 的 skills、templates、references、plugin manifests。
- Produces: `python3 scripts/check-ui-workflows.py [group]`；group 為 `capture`、`design-system`、`build`、`regression`、`release` 或省略代表全部。

- [ ] **Step 1: 寫入會檢查缺失能力的驗證器**

驗證器使用下列 group contract：

```python
GROUPS = {
    "capture": {
        "files": [
            "plugins/sg-dev-skills/skills/reference-to-ui-spec/references/capture-ui-evidence.md",
            "plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-evidence-manifest.md",
        ],
        "tokens": {
            "plugins/sg-dev-skills/skills/reference-to-ui-spec/SKILL.md": [
                "捕捉 UI 證據",
                "references/capture-ui-evidence.md",
                "templates/ui-evidence-manifest.md",
            ],
        },
    },
    "design-system": {
        "files": [
            "plugins/sg-dev-skills/skills/reference-to-ui-spec/references/extract-ui-design-system.md",
            "plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-design-system.md",
        ],
        "tokens": {
            "plugins/sg-dev-skills/skills/reference-to-ui-spec/SKILL.md": [
                "抽取設計系統",
                "references/extract-ui-design-system.md",
                "templates/ui-design-system.md",
            ],
        },
    },
    "build": {
        "files": [],
        "tokens": {
            "plugins/sg-dev-skills/skills/build-ui-from-spec/SKILL.md": [
                "reuse map",
                "deterministic",
                "可重現觸發",
            ],
        },
    },
    "regression": {
        "files": [
            "plugins/sg-dev-skills/skills/visual-ui-qa/references/automated-visual-regression.md",
            "plugins/sg-dev-skills/skills/visual-ui-qa/templates/ui-regression-plan.md",
        ],
        "tokens": {
            "plugins/sg-dev-skills/skills/visual-ui-qa/SKILL.md": [
                "自動視覺回歸",
                "references/automated-visual-regression.md",
                "templates/ui-regression-plan.md",
            ],
        },
    },
}
```

`release` 另外驗證：

- 兩份 `plugins/sg-dev-skills` manifests 都是 `0.10.0`。
- Claude marketplace 的 `sg-dev-skills` 描述包含新增能力。
- Claude manifest 仍為 10 個 skill entries。
- 追蹤中的新增 UI 文件不包含目前 checkout 的絕對路徑字串。

- [ ] **Step 2: 執行 validator 並確認正確失敗**

Run:

```bash
python3 scripts/check-ui-workflows.py
```

Expected: exit 1，列出六個缺失 resource、三個 skill routing 缺口與 `0.10.0` 版本缺口；不是 Python 語法或路徑解析錯誤。

- [ ] **Step 3: 驗證未知 group 會失敗**

Run:

```bash
python3 scripts/check-ui-workflows.py unknown
```

Expected: exit 2，顯示可用 group。

---

### Task 2: 新增 UI 證據捕捉能力

**Files:**
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/references/capture-ui-evidence.md`
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-evidence-manifest.md`
- Modify: `plugins/sg-dev-skills/skills/reference-to-ui-spec/SKILL.md`
- Modify: `plugins/sg-dev-skills/skills/reference-to-ui-spec/agents/openai.yaml`

**Interfaces:**
- Consumes: website、video、HTML、image 或 executable UI reference。
- Produces: 依 `ui-evidence-manifest.md` 填寫的 source、environment、full-page/section/motion/state evidence。

- [ ] **Step 1: 保留 Task 1 的 capture RED 證據**

Run:

```bash
python3 scripts/check-ui-workflows.py capture
```

Expected: exit 1，原因為 capture reference、template 與 SKILL route 尚不存在。

- [ ] **Step 2: 寫最小 capture reference**

內容必須以命令式繁體中文涵蓋：

- source、rights、timestamp、viewport 與 observable boundary。
- full-page 先於 section crops，crops 來自同一張完整頁面且不得漏列區段。
- video 技術 metadata 與依互動節點選代表影格。
- HTML/CSS/JS 可存取時以原始行為為證據。
- state matrix、asset provenance、observations、assumptions、missing evidence。
- 工具只能依 runtime 實際能力選用，不保證 `ffmpeg`、瀏覽器或特定測試工具存在。

- [ ] **Step 3: 寫 evidence manifest 模板**

模板固定包含：

```markdown
# UI Evidence Manifest

## Source And Rights Boundary
## Capture Environment
## Full-Page And Section Evidence
## Motion Evidence
## State And Interaction Matrix
## Asset Provenance
## Observations
## Assumptions
## Missing Evidence
```

- [ ] **Step 4: 在 SKILL.md 加入模式路由**

加入三模式路由表，capture 列必須直接連結新 reference 與 template；一般 spec 模式仍使用既有 `templates/ui-spec.md`。

- [ ] **Step 5: 更新 OpenAI metadata**

`short_description` 與 `default_prompt` 必須能表達「捕捉參考、整理規格或抽取設計系統」，不加入其他選填欄位。

- [ ] **Step 6: 執行 GREEN**

Run:

```bash
python3 scripts/check-ui-workflows.py capture
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/reference-to-ui-spec
```

Expected: 兩個 commands 都 exit 0。

---

### Task 3: 新增設計系統抽取能力

**Files:**
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/references/extract-ui-design-system.md`
- Create: `plugins/sg-dev-skills/skills/reference-to-ui-spec/templates/ui-design-system.md`
- Modify: `plugins/sg-dev-skills/skills/reference-to-ui-spec/SKILL.md`

**Interfaces:**
- Consumes: evidence manifest、UI spec、HTML/CSS、tokens、component library 或多頁 reference。
- Produces: semantic design system、component inventory、reuse/one-off mapping 與 unresolved decisions。

- [ ] **Step 1: 確認 design-system RED**

Run:

```bash
python3 scripts/check-ui-workflows.py design-system
```

Expected: exit 1，原因為 design-system reference、template 與 route 尚未完整。

- [ ] **Step 2: 寫 extraction reference**

內容涵蓋：

- 程式碼 token 優先於 screenshot estimate。
- primitive、semantic、component token 分層。
- typography、spacing、radius、elevation、motion、breakpoint 與 asset/icon rules。
- component、variant、state、responsive behavior、content rule。
- reusable pattern 與 one-off composition 分離。
- observed、inferred、proposed 三種 certainty。
- 只有目標專案已有 schema 時才輸出對應 `tokens.json`。

- [ ] **Step 3: 寫 design system 模板**

模板固定包含：

```markdown
# UI Design System

## Design Principles
## Source And Evidence Boundary
## Token Layers
## Typography And Layout
## Motion
## Component Inventory
## Variants And States
## Responsive Patterns
## Asset And Icon Rules
## Reuse Map
## One-Off Compositions
## Unresolved Decisions
```

- [ ] **Step 4: 完成 SKILL route 並執行 GREEN**

Run:

```bash
python3 scripts/check-ui-workflows.py design-system
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/reference-to-ui-spec
```

Expected: 兩個 commands 都 exit 0。

- [ ] **Step 5: Commit reference workflow**

```bash
git add scripts/check-ui-workflows.py plugins/sg-dev-skills/skills/reference-to-ui-spec
git commit -m "feat: 擴充 UI 證據與設計系統工作流"
```

---

### Task 4: 補強 UI build 的可重用與可測交接

**Files:**
- Modify: `plugins/sg-dev-skills/skills/build-ui-from-spec/SKILL.md`
- Modify: `plugins/sg-dev-skills/skills/build-ui-from-spec/templates/ui-build-brief.md`
- Modify: `plugins/sg-dev-skills/skills/build-ui-from-spec/agents/openai.yaml`

**Interfaces:**
- Consumes: optional `ui-design-system.md`、project tokens/components 與 regression coverage needs。
- Produces: reuse map、deterministic state triggers 與 tested-state handoff。

- [ ] **Step 1: 確認 build RED**

Run:

```bash
python3 scripts/check-ui-workflows.py build
```

Expected: exit 1，列出 `reuse map`、`deterministic` 與 `可重現觸發` 契約缺口。

- [ ] **Step 2: 修改 build skill 與 brief**

在 project-first 與驗證段加入：

- 先列 design system／tokens／components 的 reuse map。
- 對 regression 所需 state 使用既有 fixture、Storybook、test route 或 mock。
- 固定資料、時間、locale、timezone、theme、animation 與 network outcome 中實際需要的項目。
- 不為單次畫面建立額外抽象框架。
- 交付列出每個 viewport/state/theme 的可重現觸發方式與未穩定項目。

在 `ui-build-brief.md` 加入 `Design System And Reuse Map`、`Deterministic Test States` 與 `Verification Triggers` 欄位。

- [ ] **Step 3: 更新 metadata 並執行 GREEN**

Run:

```bash
python3 scripts/check-ui-workflows.py build
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/build-ui-from-spec
```

Expected: 兩個 commands 都 exit 0。

- [ ] **Step 4: Commit build handoff**

```bash
git add plugins/sg-dev-skills/skills/build-ui-from-spec
git commit -m "feat: 補強 UI 實作的可測交接"
```

---

### Task 5: 新增自動視覺回歸能力

**Files:**
- Create: `plugins/sg-dev-skills/skills/visual-ui-qa/references/automated-visual-regression.md`
- Create: `plugins/sg-dev-skills/skills/visual-ui-qa/templates/ui-regression-plan.md`
- Modify: `plugins/sg-dev-skills/skills/visual-ui-qa/SKILL.md`
- Modify: `plugins/sg-dev-skills/skills/visual-ui-qa/agents/openai.yaml`

**Interfaces:**
- Consumes: executable UI、approved baseline、runner、coverage matrix 與 deterministic triggers。
- Produces: regression plan，以及使用者要求實作時的 test/config/CI changes。

- [ ] **Step 1: 確認 regression RED**

Run:

```bash
python3 scripts/check-ui-workflows.py regression
```

Expected: exit 1，原因為 regression reference、template 與 route 尚不存在。

- [ ] **Step 2: 寫 automated regression reference**

內容涵蓋：

- 沿用專案 runner，不擅自更換 stack。
- 最小 `viewport × theme × state × interaction` matrix。
- 固定 data/time/locale/timezone/font/animation/network。
- baseline 必須人工確認正確，不能把首次輸出自動核准。
- threshold 只吸收 renderer noise；mask 只能窄範圍遮蔽真正不可固定的內容。
- CI 保留 expected、actual、diff 與重現 command。
- baseline 更新是顯式 reviewed action。

- [ ] **Step 3: 寫 regression plan 模板**

模板固定包含：

```markdown
# UI Regression Plan

## Scope And Baseline Authority
## Runner And Start Commands
## Deterministic Environment
## Coverage Matrix
## Threshold And Mask Rules
## Artifact Paths
## Local Commands
## CI Commands
## Baseline Update Procedure
## Known Nondeterminism
## Verification Boundary
```

- [ ] **Step 4: 在 SKILL.md 加入人工／自動模式路由並更新 metadata**

自動模式直接連結新 reference 與 template；人工模式維持既有 `ui-qa-report.md`。

- [ ] **Step 5: 執行 GREEN**

Run:

```bash
python3 scripts/check-ui-workflows.py regression
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-dev-skills/skills/visual-ui-qa
```

Expected: 兩個 commands 都 exit 0。

- [ ] **Step 6: Commit regression workflow**

```bash
git add plugins/sg-dev-skills/skills/visual-ui-qa
git commit -m "feat: 新增自動視覺回歸工作流"
```

---

### Task 6: 發佈 metadata、文件與 pre-commit 契約

**Files:**
- Modify: `plugins/sg-dev-skills/.claude-plugin/plugin.json`
- Modify: `plugins/sg-dev-skills/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `docs/CONVENTIONS.md`
- Modify: `docs/HANDOFF.md`
- Modify: `docs/TOPIC-MAP.md`
- Modify: `scripts/hooks/pre-commit`

**Interfaces:**
- Consumes: 完成的三個 UI workflow。
- Produces: `sg-dev-skills 0.10.0` 雙平台發佈描述與永久 validation gate。

- [ ] **Step 1: 確認 release RED**

Run:

```bash
python3 scripts/check-ui-workflows.py release
```

Expected: exit 1，列出兩份 plugin manifest version 與 Claude marketplace 描述尚未同步。

- [ ] **Step 2: 同步版本與描述**

- 兩份 plugin manifest 改為 `0.10.0`。
- Claude skills array 仍維持 10 entries。
- 描述加入 UI evidence、design system 與 regression，但不窮舉內部 reference。
- Claude marketplace 同步使用者可見描述；Codex marketplace 不新增 schema 未定義的 version 或 description。

- [ ] **Step 3: 更新 repository docs**

- README 的三階段 workflow 說明新增子能力。
- TOPIC-MAP 維持三入口並記錄捕捉／抽取／自動回歸的歸屬。
- CONVENTIONS 說明子流程放 references/templates，不增加 workflow entry。
- HANDOFF 更新 `sg-dev-skills 0.10.0`、10 skills 與 UI 能力狀態；保留長期實戰待辦。
- 修正舊實作計畫不正確的 ahead/behind 期望文字，改為 behind 0 且 feature commits 可存在。

- [ ] **Step 4: 將 validator 加入 pre-commit**

在 link 與 plugin compatibility 檢查後加入：

```sh
echo "[pre-commit] UI workflow 契約檢查…"
python3 scripts/check-ui-workflows.py
```

- [ ] **Step 5: 執行 release GREEN**

Run:

```bash
python3 scripts/check-ui-workflows.py release
python3 scripts/check-ui-workflows.py
```

Expected: 兩個 commands 都 exit 0。

- [ ] **Step 6: Commit release metadata**

```bash
git add .claude-plugin/marketplace.json README.md docs/CONVENTIONS.md docs/HANDOFF.md docs/TOPIC-MAP.md docs/superpowers/plans/2026-07-28-three-layer-ui-generation.md plugins/sg-dev-skills/.claude-plugin/plugin.json plugins/sg-dev-skills/.codex-plugin/plugin.json scripts/hooks/pre-commit
git commit -m "docs: 發佈 UI 證據與回歸能力"
```

---

### Task 7: 完整驗證、push 與 PR 更新

**Files:**
- Verify all changed paths。

**Interfaces:**
- Produces: clean pushed feature branch and updated PR #1。

- [ ] **Step 1: 驗證三個 skills**

```bash
for skill in reference-to-ui-spec build-ui-from-spec visual-ui-qa; do
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
    "plugins/sg-dev-skills/skills/$skill"
done
```

Expected: 3/3 pass。

- [ ] **Step 2: 執行 repository validators**

```bash
python3 scripts/check-ui-workflows.py
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
git diff --check
```

Expected: 全部 exit 0；links 為 0 broken、0 cross-plugin warnings。

- [ ] **Step 3: 驗證 manifest 與 portable paths**

```bash
python3 - <<'PY'
import json
from pathlib import Path

claude = json.loads(Path("plugins/sg-dev-skills/.claude-plugin/plugin.json").read_text())
codex = json.loads(Path("plugins/sg-dev-skills/.codex-plugin/plugin.json").read_text())
assert claude["version"] == codex["version"] == "0.10.0"
assert len(claude["skills"]) == 10
for skill in ("reference-to-ui-spec", "build-ui-from-spec", "visual-ui-qa"):
    assert Path("plugins/sg-dev-skills/skills", skill, "SKILL.md").is_file()
print("manifest and skill count: pass")
PY

python3 - <<'PY'
from pathlib import Path

root = str(Path.cwd().resolve())
paths = [Path("plugins/sg-dev-skills"), Path("README.md"), Path("docs")]
for path in paths:
    files = path.rglob("*") if path.is_dir() else [path]
    for file in files:
        if file.is_file() and root in file.read_text(errors="ignore"):
            raise SystemExit(f"absolute checkout path found: {file}")
print("portable paths: pass")
PY
```

Expected: manifest check prints pass；absolute path scan finds nothing。

- [ ] **Step 4: 最終狀態與 push**

```bash
git status --short --branch
git rev-list --left-right --count origin/main...HEAD
git push
```

Expected: push 前 worktree clean；relative to `origin/main` 為 behind 0 且 ahead 大於 0；push 完成後 feature branch 與 origin feature branch 同步，PR #1 自動更新。
