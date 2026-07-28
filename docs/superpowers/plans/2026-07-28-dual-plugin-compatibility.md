# Claude Code and Codex Dual Plugin Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all three sg-skills plugins independently installable by both Claude Code and Codex while sharing one canonical copy of every skill.

**Architecture:** Rename plugin roots to their public plugin identifiers, flatten each plugin's skill hubs directly under `skills/`, and place one Claude manifest plus one Codex manifest in each root. Keep separate platform marketplace manifests and validate their shared names, versions, source paths, and skill layout with a repository-owned checker.

**Tech Stack:** JSON manifests, Markdown Agent Skills, Python 3 validation scripts, Claude Code CLI, Codex CLI, Git.

## Global Constraints

- Keep exactly three independently installable plugins: `sg-game-dev-skills`, `sg-unity-dev-skills`, and `sg-dev-skills`.
- Share one canonical copy of every skill; do not add copied trees, symlinks, or generated plugin artifacts.
- Do not change skill knowledge content or triggering descriptions.
- Do not add MCP servers, apps, hooks, or unrelated plugin capabilities.
- Bump each plugin by one patch release for the packaging change and use the same version in both platform manifests.

---

### Task 1: Add a Cross-Platform Structure Checker

**Files:**
- Create: `scripts/check-plugin-compat.py`

**Interfaces:**
- Consumes: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and both platform manifests below each expected plugin root.
- Produces: exit code `0` with a success summary, or exit code `1` with one line per structural incompatibility.

- [ ] **Step 1: Create the checker with exact invariants**

Implement a Python 3 script using only the standard library. Define the expected mapping:

```python
EXPECTED_PLUGINS = {
    "sg-game-dev-skills": "plugins/sg-game-dev-skills",
    "sg-unity-dev-skills": "plugins/sg-unity-dev-skills",
    "sg-dev-skills": "plugins/sg-dev-skills",
}
```

For each plugin, require:

- `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`
- matching `name`, `version`, `description`, and `author`
- Codex `skills == "./skills"`
- every direct child of `skills/` to contain `SKILL.md`
- no `SKILL.md` below a nested child of `skills/`
- both marketplaces to contain exactly the three expected names
- each source path to resolve to the expected plugin root
- Codex entries to contain `AVAILABLE`, `ON_INSTALL`, and `Developer Tools`

- [ ] **Step 2: Run the checker against the current layout**

Run:

```bash
python3 scripts/check-plugin-compat.py
```

Expected: FAIL because `.agents/plugins/marketplace.json`, Codex manifests, normalized plugin roots, and flat skill hubs do not exist yet.

---

### Task 2: Normalize Plugin Roots and Skill Layout

**Files:**
- Move: `plugins/game-dev` → `plugins/sg-game-dev-skills`
- Move: `plugins/unity-dev` → `plugins/sg-unity-dev-skills`
- Move: `plugins/dev` → `plugins/sg-dev-skills`
- Move: every existing hub folder from `skills/<category>/<hub>` → `skills/<hub>`
- Modify: relative Markdown links affected by removing the category directory level
- Modify: `.claude-plugin/marketplace.json`
- Modify: all three `.claude-plugin/plugin.json` files

**Interfaces:**
- Consumes: existing skill hubs with their `references/` and `templates/`.
- Produces: three plugin roots whose direct `skills/` children are independently discoverable skill folders.

- [ ] **Step 1: Move plugin roots and complete skill hub folders**

Use `git mv` so history remains traceable. Move each hub as an intact directory, including its resources, then remove empty category directories.

- [ ] **Step 2: Update Claude manifests and marketplace**

Set Claude marketplace sources to:

```json
"./plugins/sg-game-dev-skills"
"./plugins/sg-unity-dev-skills"
"./plugins/sg-dev-skills"
```

Set each Claude manifest's `skills` array to its direct skill paths, for example:

```json
"skills": [
  "./skills/game-tooling",
  "./skills/game-architecture"
]
```

- [ ] **Step 3: Repair only links broken by the moves**

Run:

```bash
python3 scripts/check-links.py
```

Expected initially: FAIL only for relative paths whose number of parent segments changed.

Update those paths without changing prose, then rerun until it reports zero broken links and zero cross-plugin warnings.

- [ ] **Step 4: Validate Claude packaging**

Run:

```bash
claude plugin validate .
```

Expected: PASS for the marketplace and all three moved plugin sources.

---

### Task 3: Add Codex Manifests and Marketplace

**Files:**
- Create: `plugins/sg-game-dev-skills/.codex-plugin/plugin.json`
- Create: `plugins/sg-unity-dev-skills/.codex-plugin/plugin.json`
- Create: `plugins/sg-dev-skills/.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`

**Interfaces:**
- Consumes: the public metadata and versions from corresponding Claude manifests.
- Produces: Codex manifests accepted by plugin ingestion and a repo marketplace named `sg-skills`.

- [ ] **Step 1: Add minimal Codex manifests**

Each manifest must include:

```json
{
  "name": "<matching-plugin-name>",
  "version": "<matching-Claude-version>",
  "description": "<matching-Claude-description>",
  "author": {
    "name": "Stone",
    "email": "seaglegames@gmail.com"
  },
  "skills": "./skills",
  "repository": "https://github.com/stoneshih99/sg-skills",
  "interface": {
    "displayName": "<human-readable-name>",
    "shortDescription": "<concise-subtitle>",
    "longDescription": "<plugin-description>",
    "developerName": "Stone",
    "category": "Developer Tools",
    "capabilities": ["Guidance"],
    "defaultPrompt": ["<one representative prompt>"]
  }
}
```

Do not add optional URLs, icons, apps, MCP servers, or hooks.

- [ ] **Step 2: Add the Codex marketplace**

Create a marketplace named `sg-skills` with `interface.displayName` set to `SG Skills`. Add the three plugin entries in the same order as the Claude marketplace. Each source uses:

```json
{
  "source": "local",
  "path": "./plugins/<plugin-name>"
}
```

Each entry uses:

```json
"policy": {
  "installation": "AVAILABLE",
  "authentication": "ON_INSTALL"
},
"category": "Developer Tools"
```

- [ ] **Step 3: Run repository and official validators**

Run:

```bash
python3 scripts/check-plugin-compat.py
python3 /Users/stone/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/sg-game-dev-skills
python3 /Users/stone/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/sg-unity-dev-skills
python3 /Users/stone/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/sg-dev-skills
```

Expected: all four commands PASS.

---

### Task 4: Update Installation Documentation and Commit Checks

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `docs/CONVENTIONS.md`
- Modify: `docs/HANDOFF.md`
- Modify: `docs/TOPIC-MAP.md`
- Modify: `scripts/hooks/pre-commit`

**Interfaces:**
- Consumes: final normalized paths and the two marketplace install commands.
- Produces: accurate contributor instructions and automatic local compatibility checks.

- [ ] **Step 1: Replace stale repository paths**

Update references from `plugins/game-dev`, `plugins/unity-dev`, and `plugins/dev` to normalized roots. Update category-nested skill examples to direct `skills/<hub>` paths.

- [ ] **Step 2: Document both installation flows**

Keep current Claude commands and add:

```bash
codex plugin marketplace add stoneshih99/sg-skills
codex plugin add sg-game-dev-skills@sg-skills
codex plugin add sg-unity-dev-skills@sg-skills
codex plugin add sg-dev-skills@sg-skills
```

Explain that both platforms install the same three independently selectable plugins.

- [ ] **Step 3: Add compatibility validation to pre-commit**

Run the repository-owned checker before platform CLI validation:

```bash
python3 scripts/check-plugin-compat.py
```

Keep existing link and Claude validation checks.

- [ ] **Step 4: Verify documentation and hook behavior**

Run:

```bash
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
scripts/hooks/pre-commit
```

Expected: all commands PASS.

---

### Task 5: Perform Isolated Installation Smoke Tests

**Files:**
- No repository files created or modified.

**Interfaces:**
- Consumes: the completed local marketplace and plugin trees.
- Produces: evidence that Codex can add the marketplace and all three plugins without changing the user's normal Codex configuration.

- [ ] **Step 1: Create an isolated temporary Codex home**

Use `mktemp -d` and set `CODEX_HOME` only for the smoke-test commands. Do not reuse or overwrite the user's normal Codex configuration.

- [ ] **Step 2: Add the local marketplace and three plugins**

Run `codex plugin marketplace add /Volumes/WorkSpace/Projects/Github/sg-skills`, then add all three `<plugin>@sg-skills` identifiers under the isolated `CODEX_HOME`.

Expected: each add command succeeds and `codex plugin list` shows the three plugins.

- [ ] **Step 3: Run final repository verification**

Run:

```bash
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
git diff --check
git status --short
```

Expected: all validations pass; status contains only intended compatibility, documentation, plan, and moved-file changes.

- [ ] **Step 4: Commit implementation**

Stage only the intended paths and commit with a concise project-style message describing dual Claude Code and Codex plugin installation support. Do not push unless the user requests it.
