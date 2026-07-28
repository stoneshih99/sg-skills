# Claude Code 與 Codex 雙 Plugin 相容設計

## 目標

讓同一個 repository 內的三個 plugin 同時可由 Claude Code 與 Codex 安裝，且兩邊共用同一份 skill 內容：

- `sg-game-dev-skills`
- `sg-unity-dev-skills`
- `sg-dev-skills`

完成後不以複製或生成副本維持雙平台內容，避免 skill 漂移。

## 目錄設計

將 plugin 目錄名稱與 plugin identifier 對齊：

| 現有目錄 | 新目錄 |
| --- | --- |
| `plugins/game-dev` | `plugins/sg-game-dev-skills` |
| `plugins/unity-dev` | `plugins/sg-unity-dev-skills` |
| `plugins/dev` | `plugins/sg-dev-skills` |

每個 plugin 採相同結構：

```text
plugins/<plugin-name>/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
└── skills/
    ├── <skill-a>/SKILL.md
    └── <skill-b>/SKILL.md
```

目前 category 中介層會移除。例如：

```text
plugins/game-dev/skills/architecture/game-architecture
→ plugins/sg-game-dev-skills/skills/game-architecture
```

只移動 skill hub 及其既有 `references/`、`templates/`；不改寫 skill 的領域內容。移動後只修正因路徑改變而失效的相對連結。

## Manifest 與 Marketplace

每個 plugin：

- Claude manifest 保留 `.claude-plugin/plugin.json`，更新 `skills` 與來源路徑。
- Codex manifest 新增 `.codex-plugin/plugin.json`，使用同一個 `name`、`version`、`description` 與 `author`。
- Codex 的 `skills` 指向 `./skills`，並補齊必要的 `interface` metadata。

Repository 根目錄保留 Claude marketplace：

```text
.claude-plugin/marketplace.json
```

並新增 Codex repo marketplace：

```text
.agents/plugins/marketplace.json
```

兩個 marketplace 都列出相同三個 plugin；各自使用平台要求的 source 格式。Codex entries 明確包含：

- `policy.installation: AVAILABLE`
- `policy.authentication: ON_INSTALL`
- `category: Developer Tools`

## 安裝介面

README 同時提供：

```text
claude plugin marketplace add stoneshih99/sg-skills
claude plugin install <plugin>@sg-skills
```

以及 Codex 對應的 marketplace 設定與：

```text
codex plugin marketplace add stoneshih99/sg-skills
codex plugin add <plugin>@sg-skills
```

三個 plugin 維持各自選裝，不新增聚合 plugin。

## 驗證

修改後必須通過：

1. `python3 scripts/check-links.py`
2. `claude plugin validate .`
3. Codex plugin schema validator，對三個 plugin 各跑一次
4. JSON parse 與跨平台一致性檢查：
   - plugin 名稱一致
   - 版本一致
   - marketplace 恰好列出三個預期 plugin
   - source 指向存在且名稱相符的目錄
5. 在隔離的暫存設定目錄執行 Codex marketplace 與三個 plugin 的安裝 smoke test，不改動使用者既有 Codex 設定
6. `git diff --check`

pre-commit hook 會加入可在 repository 內重跑的結構檢查；若某平台 CLI 未安裝，顯示明確提示，不以假成功取代平台驗證。

## 範圍限制

- 不修改 skill 的知識內容或觸發描述。
- 不新增 skill 副本、symlink 或發佈產物。
- 不加入 MCP、app、hook 或其他 plugin 功能。
- 不改變三個 plugin 的定位與拆分方式。
