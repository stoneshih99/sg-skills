# Ship Small Game Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一個可從遊戲構想到 Release Candidate Build、具重大決策閘門與證據邊界的 `ship-small-game` 總控 workflow。

**Architecture:** 在 `sg-game-dev-skills` 增加單一可執行 workflow，透過七階段狀態、四份核心交付物與部門交接契約協調既有 hubs，以及選配的 Unity／UI plugins。專業知識不複製進總控；機器可查的檔案、路由、版本與可攜路徑由獨立 validator 強制。

**Tech Stack:** Markdown Agent Skills、YAML OpenAI skill metadata、JSON Claude/Codex plugin manifests、Python 3 repository validators、Bash pre-commit hook、Claude Code Plugin CLI、Codex Plugin CLI。

## Global Constraints

- 目標是可從開始玩到結局、通過驗收並產生 Release Candidate Build 的小型完整遊戲。
- 商店頁、平台認證、法務文件、營運活動與發布後監控不在範圍。
- 可逆低成本決策可自主執行；核心玩法、範圍、技術選型、資產授權、破壞性遷移、平台與正式發佈必須核准。
- 總控保持引擎中立；Unity 與 UI 能力只能在對應 plugin 可用時交接執行。
- 專業內容留在既有 hubs；跨 plugin 只用文字提及，不建立相對連結。
- 只維護 `game-brief`、`delivery-roadmap`、`acceptance-matrix`、`production-status` 四份核心交付物。
- 無執行證據只能標記 Unverified；缺少必要能力標記 Blocked；不得推測為完成。
- `sg-game-dev-skills` 兩份 manifest 同步升級為 `0.27.0`。
- repository 內容不得寫入 checkout 絕對路徑。

---

### Task 1: 建立無總控 workflow 的行為基線

**Files:**
- Verify only: existing repository and current installed skills

**Interfaces:**
- Consumes: three pressure scenarios below, without loading `ship-small-game`
- Produces: baseline observations for the minimum behavior the new workflow must change

- [ ] **Step 1: 執行模糊新遊戲 baseline**

以全新 subagent、不要提供預期答案或設計結論，送出：

```text
我要做一款 Unity 小型動作遊戲，從企畫、畫面、程式、測試一路做到可以交付的 Build。請現在開始帶我完成。
```

記錄是否直接寫程式、是否先界定開始到結局、是否提出重大決策閘門，以及是否定義 Build 與驗收證據。

- [ ] **Step 2: 執行中途接手 baseline**

```text
請接手這個做到一半的遊戲專案。現在有一些場景和程式，但文件不完整；把它完成並交付。
```

記錄是否先以 repository 證據重建進度，或把檔案存在誤認為功能完成。

- [ ] **Step 3: 執行受阻專案 baseline**

```text
遊戲功能差不多了，但部分圖片來源不明，這台機器也沒有目標平台 SDK。請完成測試並產出正式版本。
```

記錄是否正確標示 Blocked／Unverified，或假裝資產與 Build 已通過。

- [ ] **Step 4: 整理 RED 判準**

後續 skill 至少要修正以下任一實際觀察到的失敗；若 baseline 已自然做到其中一項，仍保留其餘可觀察缺口：

```text
- 未建立 Game Contract 就展開實作
- 缺少七階段與依賴順序
- 沒有四份核心交付物
- 重大決策未停在核准閘門
- 未按部門能力交接
- 將 Unverified 或 Blocked 誤報為完成
```

Expected: 取得具體 baseline 行為證據；本 task 不修改檔案、不建立 commit。

---

### Task 2: 建立遊戲交付 workflow 靜態契約

**Files:**
- Create: `scripts/check-game-delivery-workflow.py`

**Interfaces:**
- Consumes: repository root、預期版本 `0.27.0`、Claude skill count `6`
- Produces: `python3 scripts/check-game-delivery-workflow.py [core routing release]`；契約缺失回傳 1，未知 group 回傳 2

- [ ] **Step 1: 寫入 validator**

依 `scripts/check-ui-workflows.py` 的結構建立 checker，固定常數、七階段與 groups：

```python
ROOT = Path(__file__).resolve().parent.parent
EXPECTED_VERSION = "0.27.0"
EXPECTED_SKILL_COUNT = 6
STAGES = [
    "Preflight",
    "Game Contract",
    "Production Blueprint",
    "Vertical Slice",
    "Content Complete",
    "Quality Complete",
    "Release Candidate",
]

GROUPS = {
    "core": {
        "files": [
            "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/agents/openai.yaml",
            "plugins/sg-game-dev-skills/skills/ship-small-game/references/stage-gates.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/game-brief.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/delivery-roadmap.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/acceptance-matrix.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/production-status.md",
        ],
        "tokens": {
            "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md": [
                "Preflight",
                "Game Contract",
                "Production Blueprint",
                "Vertical Slice",
                "Content Complete",
                "Quality Complete",
                "Release Candidate",
                "重大決策",
                "Verified",
                "Unverified",
                "Blocked",
            ],
        },
    },
    "routing": {
        "files": [
            "plugins/sg-game-dev-skills/skills/ship-small-game/references/department-routing.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/references/recovery-and-scope-control.md",
        ],
        "tokens": {
            "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md": [
                "references/department-routing.md",
                "references/recovery-and-scope-control.md",
            ],
        },
    },
}
```

`check_core_contract()` 不只找 token，還必須：

- 解析 `stage-gates.md` 的二級 heading，確認七階段順序完全等於 `STAGES`。
- 在每個 stage block 內依序確認進入條件、必做工作、核准閘門、完成證據、下一階段五欄，並檢查相鄰 stage 的進入與下一階段契約。
- 在 `Content Complete` 的核准閘門檢查停止新增功能，在 `Quality Complete` 的完成證據檢查程式／完整流程／視覺／效能／存檔／玩測，在 `Release Candidate` 的完成證據檢查可執行 Build。
- 在 `SKILL.md` 的階段 section 檢查七階段箭頭順序與「不可跳過中間階段」規則。
- 解析四份模板的 headings 與 Markdown tables；roadmap 須有七階段狀態列，acceptance matrix 須拆開 accepted risk owner 與 reason，production status 須有 `Last Updated`。

`check_routing_contract()` 必須解析 handoff 五欄的順序，以及 recovery table 的三欄與七個情境；不能只驗證 reference 連結存在。

`check_release()` 必須驗證：

```python
assert claude_manifest["version"] == "0.27.0"
assert codex_manifest["version"] == "0.27.0"
assert len(claude_manifest["skills"]) == 6
assert "./skills/ship-small-game" in claude_manifest["skills"]
assert "完整遊戲" in claude_marketplace_entry["description"]
```

portable path scan 以 `git ls-files` 列出追蹤檔案，涵蓋 marketplace metadata、`CLAUDE.md`、`README.md`、`docs/` 與 `plugins/` 內的文字資產；拒絕目前 checkout root 與常見使用者 home／mounted-volume checkout 絕對路徑。checker source 不在掃描範圍，web URL 與 `/usr/bin` 等合理命令不應被誤判。

實作時不要直接用 `assert`；沿用 UI checker 的 `errors.append(...)`、JSON 錯誤處理與 group selection。

- [ ] **Step 2: 驗證未知 group**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py unknown
```

Expected: exit 2，stderr 列出 `core, routing, release`。

- [ ] **Step 3: 驗證 RED**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py
```

Expected: exit 1，至少報告缺少 `ship-small-game/SKILL.md`、resources、manifest entry 與 `0.27.0`。

- [ ] **Step 4: 檢查 script 語法與格式**

Run:

```bash
python3 -m py_compile scripts/check-game-delivery-workflow.py
git diff --check
```

Expected: exit 0。

- [ ] **Step 5: Commit validator**

```bash
git add scripts/check-game-delivery-workflow.py
git commit -m "test: 加入完整遊戲交付契約檢查"
```

---

### Task 3: 建立總控核心、七階段與四份交付物

**Files:**
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/agents/openai.yaml`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/references/stage-gates.md`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/templates/game-brief.md`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/templates/delivery-roadmap.md`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/templates/acceptance-matrix.md`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/templates/production-status.md`
- Modify: `plugins/sg-game-dev-skills/.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: a vague game idea or an existing project; optional installed game-dev、Unity and UI capabilities
- Produces: a resumable seven-stage execution state backed by four project-owned Markdown artifacts

- [ ] **Step 1: 使用 skill initializer 建立 canonical folder**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
  ship-small-game \
  --path plugins/sg-game-dev-skills/skills \
  --resources references \
  --interface display_name="Ship Small Game" \
  --interface short_description="把小型遊戲從構想推進到可驗證的交付 Build 流程" \
  --interface default_prompt="請使用 \$ship-small-game 協調企畫、實作、測試與 Build，把這款小型遊戲推進到可交付狀態。"
```

Expected: 建立 `SKILL.md`、`agents/openai.yaml` 與 `references/`，沒有 examples 或額外 README。

- [ ] **Step 2: 寫入最小 SKILL.md**

frontmatter 使用：

```yaml
---
name: ship-small-game
description: Use when 使用者要把小型遊戲從構想或未完成專案一路做到可交付 Build，包含完整遊戲、垂直切片後擴充、跨企畫美術程式測試協調、接手半成品或判定是否能發佈
---
```

body 必須保持精簡，包含：

```markdown
# Ship Small Game

## 定位

這是小型完整遊戲的總控 workflow。負責階段、範圍、交接、核准與證據；專業決策交給既有 hubs，不重寫其內容。

## 開始前

先讀 repository 指令與既有文件，盤點引擎、平台、工具、資產授權、測試及 Build 能力。既有證據優先；不要從對話假設專案狀態。

## 決策權

- 可逆且低成本的決定可自主執行並記錄。
- 核心玩法、範圍、技術選型、授權、破壞性遷移、平台與正式發佈是重大決策，必須核准。

## 階段

Preflight → Game Contract → Production Blueprint → Vertical Slice → Content Complete → Quality Complete → Release Candidate

逐階段規則讀 [stage-gates.md](references/stage-gates.md)。

## 核心交付物

複製並依專案慣例保存四份模板：

- [game-brief.md](templates/game-brief.md)
- [delivery-roadmap.md](templates/delivery-roadmap.md)
- [acceptance-matrix.md](templates/acceptance-matrix.md)
- [production-status.md](templates/production-status.md)

## 證據邊界

每項驗收只可標記 Verified、Unverified 或 Blocked。沒有執行證據不得宣告完成。
```

- [ ] **Step 3: 寫入 stage gates reference**

`stage-gates.md` 對七個階段各使用相同 schema：

```markdown
## <Stage>

- 進入條件：
- 必做工作：
- 核准閘門：
- 完成證據：
- 下一階段：
```

明確規定 Vertical Slice 必須證明端到端管線、Content Complete 後停止新增功能、Quality Complete 必須包含程式／完整流程／視覺／效能／存檔／玩測，Release Candidate 必須有可執行 Build。

- [ ] **Step 4: 寫入四份模板**

`game-brief.md` 固定 headings：

```markdown
# Game Brief
## Product Promise
## Target Player And Platform
## Core Loop
## Start-To-End Flow
## Must / Cut / Not Doing
## Definition Of Done
## Approved Major Decisions
```

`delivery-roadmap.md` 固定欄位：

```markdown
# Delivery Roadmap

## Current Stage

## Stage Status

| Stage | Status | Evidence Or Notes |
| --- | --- | --- |
| Preflight | Not Started |  |
| Game Contract | Not Started |  |
| Production Blueprint | Not Started |  |
| Vertical Slice | Not Started |  |
| Content Complete | Not Started |  |
| Quality Complete | Not Started |  |
| Release Candidate | Not Started |  |

## Work Packages

| ID | Deliverable | Department | Depends On | Verification | Status |
| --- | --- | --- | --- | --- | --- |

## Risks And Gates

## Next Executable Step
```

`acceptance-matrix.md` 固定欄位：

```markdown
# Acceptance Matrix

| Area | Acceptance | State | Evidence Or Reproduction | Accepted Risk Owner | Accepted Risk Reason |
| --- | --- | --- | --- | --- | --- |
| Gameplay |  | Unverified |  |  |  |
| Start-To-End |  | Unverified |  |  |  |
| Visual |  | Unverified |  |  |  |
| Content |  | Unverified |  |  |  |
| Code |  | Unverified |  |  |  |
| Tests |  | Unverified |  |  |  |
| Performance |  | Unverified |  |  |  |
| Save |  | Unverified |  |  |  |
| Build |  | Unverified |  |  |  |

State 僅允許 Verified、Unverified、Blocked。
```

`production-status.md` 固定 headings：

```markdown
# Production Status

## Last Updated

## Current Stage

## Completed

## In Progress

## Next

## Blocked

## Recent Decisions And Scope Changes

## Resume Here
```

- [ ] **Step 5: 加入 Claude discovery entry**

在 Claude manifest 的既有 `skills` 陣列末尾加入：

```json
"./skills/ship-small-game"
```

本 task 不修改 `0.26.1` 版本或其他 release metadata；entry 必須提前加入，讓 repository 的 plugin 相容性 pre-commit 能在 core commit 通過。

- [ ] **Step 6: 執行 core GREEN**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py core
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-game-dev-skills/skills/ship-small-game
python3 scripts/check-plugin-compat.py
git diff --check
```

Expected: 四項 exit 0。

- [ ] **Step 7: Commit core**

```bash
git add \
  plugins/sg-game-dev-skills/skills/ship-small-game \
  plugins/sg-game-dev-skills/.claude-plugin/plugin.json
git commit -m "feat: 新增小型遊戲總控骨架"
```

---

### Task 4: 補齊部門路由、受阻與恢復契約

**Files:**
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/references/department-routing.md`
- Create: `plugins/sg-game-dev-skills/skills/ship-small-game/references/recovery-and-scope-control.md`
- Modify: `plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md`

**Interfaces:**
- Consumes: current stage、installed capabilities、roadmap dependencies and evidence states
- Produces: a bounded department handoff or a smallest unblock/resume action

- [ ] **Step 1: 寫入 department routing**

建立 spec 中的部門對照表，並要求每次 handoff 使用：

```markdown
## Handoff Contract

- Input：
- Expected output：
- Dependencies：
- Verification：
- Core artifacts to update：
```

明確寫出：

- game-dev hubs 是設計與生產知識來源。
- Unity plugins 只在 Unity 專案且能力可用時執行。
- 三個 UI workflows 依 reference → build → QA 順序交接。
- 未安裝能力只形成待執行 handoff，不算完成。

- [ ] **Step 2: 寫入 recovery and scope control**

用決策表定義：

```markdown
| Condition | Disposition | Required action |
| --- | --- | --- |
| Missing engine/SDK/account/build tool | Blocked | 記錄缺口與最小解阻步驟 |
| Asset provenance unclear | Blocked for RC | 使用合法暫代資產或取得授權 |
| Verification cannot run | Unverified | 保留命令與所需環境 |
| Test fails | Not complete | 修復或經核准縮減範圍 |
| Scope grows after Content Complete | Gate required | 回到 scope cutting 並更新四份文件 |
| Existing project lacks docs | Reconstruct | 從 repository 證據重建狀態 |
| Session resumes | Resume | 執行最早且依賴已滿足的未完成項目 |
```

- [ ] **Step 3: 在 SKILL.md 加入路由**

加入：

```markdown
## 路由與恢復

- 分派專業工作前讀 [department-routing.md](references/department-routing.md)。
- 接手既有專案、範圍失控或能力受阻時讀 [recovery-and-scope-control.md](references/recovery-and-scope-control.md)。
- 每次工作完成後回寫 roadmap、acceptance matrix 與 production status。
```

- [ ] **Step 4: 執行 routing GREEN**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py core routing
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-game-dev-skills/skills/ship-small-game
python3 scripts/check-links.py
git diff --check
```

Expected: 全部 exit 0；links 為 0 broken、0 cross-plugin warnings。

- [ ] **Step 5: Commit routing**

```bash
git add plugins/sg-game-dev-skills/skills/ship-small-game
git commit -m "feat: 補齊遊戲總控的部門交接與恢復"
```

---

### Task 5: Forward-test 總控行為並關閉 baseline 缺口

**Files:**
- Modify if required: `plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md`
- Modify if required: bundled references or templates under `plugins/sg-game-dev-skills/skills/ship-small-game/`

**Interfaces:**
- Consumes: exact three pressure scenarios from Task 1 plus the completed skill
- Produces: evidence that the workflow changes behavior without leaking intended answers

- [ ] **Step 1: 以全新 subagents 重跑三個情境**

每個 subagent 只取得：

```text
Use $ship-small-game at plugins/sg-game-dev-skills/skills/ship-small-game to solve:
<Task 1 的原始使用者情境>
```

不要提供 baseline 結論、預期文件內容或設計規格。

- [ ] **Step 2: 對照可觀察成功條件**

三個情境共同檢查：

```text
- 先盤點 repository、工具與證據
- 重大決策停在核准閘門
- 使用七階段與四份核心交付物
- 專業工作形成明確 handoff
- Blocked／Unverified 沒有被宣告完成
- 下一步是依賴已滿足的最小工作
```

- [ ] **Step 3: 只修正實際暴露的漏洞**

若 Agent 跳過規則，只修改能直接阻止該行為的最小段落；不新增角色 skills、第五份狀態文件或未在 spec 內的流程。

- [ ] **Step 4: 重跑受影響情境與 validators**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py core routing
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-game-dev-skills/skills/ship-small-game
git diff --check
```

Expected: validators exit 0；受影響情境不再重現原漏洞。

- [ ] **Step 5: Commit refinements if any**

若 Task 5 產生檔案變更：

```bash
git add plugins/sg-game-dev-skills/skills/ship-small-game
git commit -m "fix: 收斂小型遊戲總控行為"
```

若沒有變更，記錄 forward-test 通過並直接進 Task 6。

---

### Task 6: 發佈 0.27.0 並接入 repository 契約

**Files:**
- Modify: `plugins/sg-game-dev-skills/.claude-plugin/plugin.json`
- Modify: `plugins/sg-game-dev-skills/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `docs/CONVENTIONS.md`
- Modify: `docs/HANDOFF.md`
- Modify: `docs/TOPIC-MAP.md`
- Modify: `scripts/hooks/pre-commit`

**Interfaces:**
- Consumes: validated `ship-small-game` workflow and `check-game-delivery-workflow.py`
- Produces: discoverable `sg-game-dev-skills@0.27.0` on Claude Code and Codex

- [ ] **Step 1: 驗證 release RED**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py release
```

Expected: exit 1，至少指出兩份版本與 marketplace 描述尚未更新。

- [ ] **Step 2: 更新兩份 plugin manifests**

Claude manifest 保留 Task 3 已加入的 skill entry，並更新版本：

```json
"version": "0.27.0",
"skills": [
  "./skills/game-tooling",
  "./skills/game-architecture",
  "./skills/game-production",
  "./skills/game-diagrams",
  "./skills/game-design",
  "./skills/ship-small-game"
]
```

Codex manifest 同步 `version: 0.27.0`，並讓 description／longDescription／defaultPrompt 可發現「完整遊戲」與「交付 Build」情境；`skills` 仍是 `"./skills"`。

- [ ] **Step 3: 更新 marketplace 與文件**

只修改 Claude marketplace 的 `sg-game-dev-skills` description，加入「完整遊戲交付」；Codex marketplace schema 不含 description／version，不修改。

README 加入總控 workflow 與七階段摘要。TOPIC-MAP 將 game-dev 新增 `ship-small-game` 的獨立 workflow ownership。CONVENTIONS 補充總控 workflow 不得複製專業 hub 內容。

HANDOFF 更新為：

```text
sg-game-dev-skills | 0.27.0 | 5 hub + 1 workflow / 90 篇 reference
合計 19 skills、152 篇 reference
```

並把「小型完整遊戲總控 workflow」加入已完成待辦。

- [ ] **Step 4: 接入 pre-commit**

在 UI workflow 檢查後加入：

```bash
echo "[pre-commit] 完整遊戲交付 workflow 契約檢查…"
python3 scripts/check-game-delivery-workflow.py
```

README 與 CONVENTIONS 的 validator 清單同步加入新 checker。

- [ ] **Step 5: 驗證 release GREEN**

Run:

```bash
python3 scripts/check-game-delivery-workflow.py release
python3 scripts/check-game-delivery-workflow.py
python3 scripts/check-ui-workflows.py
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
git diff --check
```

Expected: 全部 exit 0；links 為 0 broken、0 cross-plugin warnings。

- [ ] **Step 6: Commit release**

```bash
git add \
  plugins/sg-game-dev-skills/.claude-plugin/plugin.json \
  plugins/sg-game-dev-skills/.codex-plugin/plugin.json \
  .claude-plugin/marketplace.json \
  README.md \
  docs/CONVENTIONS.md \
  docs/HANDOFF.md \
  docs/TOPIC-MAP.md \
  scripts/hooks/pre-commit
git commit -m "docs: 發佈小型完整遊戲總控工作流"
```

---

### Task 7: 完整驗證、隔離安裝、push 與 PR 更新

**Files:**
- Verify: all changed paths

**Interfaces:**
- Consumes: released `sg-game-dev-skills@0.27.0`
- Produces: clean pushed feature branch and updated existing PR

- [ ] **Step 1: 執行所有 repository 與 skill validators**

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/sg-game-dev-skills/skills/ship-small-game
python3 scripts/check-game-delivery-workflow.py
python3 scripts/check-ui-workflows.py
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
git diff --check
```

Expected: 全部 exit 0。

- [ ] **Step 2: 驗證 manifest 與 portable paths**

```bash
python3 - <<'PY'
import json
from pathlib import Path

claude = json.loads(Path("plugins/sg-game-dev-skills/.claude-plugin/plugin.json").read_text())
codex = json.loads(Path("plugins/sg-game-dev-skills/.codex-plugin/plugin.json").read_text())
assert claude["version"] == codex["version"] == "0.27.0"
assert len(claude["skills"]) == 6
assert "./skills/ship-small-game" in claude["skills"]
print("game delivery manifest: pass")
PY

python3 scripts/check-game-delivery-workflow.py release
```

Expected: manifest snippet 印出 pass，release group 同時驗證發佈 metadata 與 repository 追蹤文字的 portable paths。

- [ ] **Step 3: 執行隔離 Codex local-install smoke**

使用系統產生的臨時目錄作為 Codex home，不修改使用者日常設定：

```bash
SMOKE_HOME="$(mktemp -d)"
CODEX_HOME="$SMOKE_HOME" codex plugin marketplace add . --json
CODEX_HOME="$SMOKE_HOME" codex plugin add sg-game-dev-skills@sg-skills --json
```

確認安裝結果版本為 `0.27.0`，並存在：

```text
skills/ship-small-game/SKILL.md
skills/ship-small-game/references/stage-gates.md
skills/ship-small-game/references/department-routing.md
skills/ship-small-game/references/recovery-and-scope-control.md
skills/ship-small-game/templates/game-brief.md
skills/ship-small-game/templates/delivery-roadmap.md
skills/ship-small-game/templates/acceptance-matrix.md
skills/ship-small-game/templates/production-status.md
```

驗證後只刪除本次建立且已解析成明確路徑的 `SMOKE_HOME`。

- [ ] **Step 4: 檢查 branch 與 commit 結構**

```bash
git status --short --branch
git rev-list --left-right --count origin/main...HEAD
git log --oneline -10
```

Expected: worktree clean；相對 `origin/main` behind 0、ahead 大於 0；設計、計畫、validator、core、routing 與 release commits 邊界清楚。

- [ ] **Step 5: Push 並確認遠端同步**

```bash
git push
git rev-parse HEAD
git rev-parse origin/codex/ui-generation-workflows
```

Expected: 兩個 SHA 完全相同；既有 PR 自動更新且 worktree 保留供 review feedback。
