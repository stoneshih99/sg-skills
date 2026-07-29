# 小型完整遊戲總控工作流設計

## 目標

新增一個可執行的 `ship-small-game` workflow，讓 Agent 能從模糊構想或既有專案出發，協調企畫、架構、內容、Unity、UI、測試與建置能力，交付一款可從開始玩到結局的小型完整遊戲。

完成的定義是：

- 核心玩法與完整流程可遊玩。
- 必要畫面、內容、設定與存檔已交付。
- 程式、視覺、效能與人工玩測有可追溯證據。
- 目標平台 Release Candidate Build 已產生。
- 未驗證或受阻項目沒有被誤報為完成。

商店頁、平台認證、法務文件、營運活動與發布後監控不在本次範圍。

## 結構裁決

### 採用：新增單一總控 workflow

在 `sg-game-dev-skills` 新增獨立的 `ship-small-game` workflow。它扮演製作人與 Game Director，只負責：

- 階段排序與範圍控制。
- 跨部門路由與交接。
- 重大決策核准。
- 驗收證據與完成判定。
- 受阻狀態與恢復入口。

專業知識仍由既有 hubs 與可用 plugins 負責，總控不重寫玩法設計、Unity API、UI 實作或測試方法。

### 不採用：擴充 `game-production`

`game-production` 是知識 hub，適合回答里程碑、資產、音效、UI 與發佈問題；它不是從構想到 Build 的長流程執行器。把總控藏在 reference 內會讓 Agent 容易只處理局部問題，缺少完整交付狀態。

### 不採用：每個職稱一個 skill

Producer、Art Director、QA Lead 與 Release Manager 會與既有 hubs 大量重疊，也會造成多條相似 description 同時觸發。部門以總控內的責任與檢查點呈現，不各自新增入口。

## 決策模型

採混合自主模式：

- 可逆、低成本、不改變產品方向的小決定，由 Agent 自主執行並記錄。
- 核心玩法、範圍、技術選型、付費或授權資產、破壞性遷移、目標平台與正式發佈，必須取得使用者核准。
- 已有專案規範、文件與實作證據優先於總控的預設值。
- 多種合理答案會造成明顯返工時，停在核准閘門，不默默替使用者選擇。

## 引擎邊界

總控保持引擎中立，放在 `sg-game-dev-skills`：

- 未知引擎時，仍可完成企畫、範圍、里程碑、驗收與部門交接。
- 偵測到 Unity 專案且 `sg-unity-dev-skills` 可用時，交接 Unity C#、資產、執行期、測試、效能與 Build 工作。
- Unity 能力不可用時，不偽造 Scene、Prefab、測試或 Build 證據；對應項目標記為 Blocked 或 Unverified。
- UI 工作依序使用 UI 規格、實作與視覺 QA workflow；未安裝 `sg-dev-skills` 時，以文字交接契約保留工作，不宣稱已完成 UI 實作。

跨 plugin 只用名稱與交接文字，不建立安裝後會斷裂的相對連結，也不在 plugin manifest 假設未支援的依賴機制。

## 七階段流程

### 1. Preflight

檢查 repository、引擎、目標平台、工具、既有文件、資產來源、授權、測試能力與 Build 環境。輸出初始狀態；缺少必要能力時明確標記。

### 2. Game Contract

收斂核心循環、目標玩家、遊戲開始與結束、完成條件、內容邊界及明確不做項目。這是第一個重大核准閘門。

### 3. Production Blueprint

拆解玩法系統、場景、UI、資產、音效、測試與 Build，建立依賴順序、風險、里程碑與驗收方式。技術選型與範圍需核准。

### 4. Vertical Slice

先完成一段具代表性的端到端體驗，使用實際玩法、UI、音效、存檔骨架與測試入口，證明內容和建置管線可行。尚未證明的能力不得直接展開成大量內容。

### 5. Content Complete

補齊從開始到結局所需內容並停止增加新功能。未完成項目只能完成、縮減或經核准移除。

### 6. Quality Complete

執行程式測試、完整流程 smoke、視覺回歸、效能檢查、存檔相容性與人工玩測。每個驗收項目記錄 Verified、Unverified 或 Blocked 及其證據。

### 7. Release Candidate

產生正式 Build、版本資訊、操作說明與已知問題。只有驗收矩陣全部通過，或使用者明確接受剩餘風險，才能宣告完成。

## 核心交付物

workflow 提供四份模板；目標專案可依既有慣例決定保存位置，所有模板只使用相對路徑。

### `game-brief`

- 產品承諾與目標玩家
- 核心循環與開始到結局
- 必做、可刪與不做項目
- 目標平台與完成定義
- 已核准的重大決策

### `delivery-roadmap`

- 七階段狀態
- 工作包、依賴與負責部門
- 風險、驗證方式與核准閘門
- 目前最小可執行下一步

### `acceptance-matrix`

- 玩法、畫面、內容、程式、測試、效能、存檔與 Build 驗收項目
- Verified／Unverified／Blocked 狀態
- 證據位置、執行命令或重現方式
- 接受風險者與理由

### `production-status`

- 目前階段與最後更新時間
- 已完成、進行中、下一步與阻塞
- 最近決策與範圍變更
- 可供新 Agent 恢復工作的交接摘要

四份交付物是專案狀態的最小集合，不再建立重複的角色報告、週報或同義待辦清單。

## 部門路由

| 工作 | 主要能力 |
|---|---|
| 核心玩法、GDD、關卡與人工玩測 | `game-design` |
| 系統、資料、AI 與網路架構 | `game-architecture` |
| 美術、音效、動畫、內容與里程碑 | `game-production` |
| 除錯、效能方法與遙測 | `game-tooling` |
| Unity C#、資產、Editor 與自動測試 | `unity-scripting` |
| Unity UI、物理、動畫、Shader 與音效 | `unity-runtime` |
| Unity 效能與 Build | `unity-optimization` |
| UI 證據、規格、實作與視覺回歸 | `reference-to-ui-spec`、`build-ui-from-spec`、`visual-ui-qa` |

每次交接都要包含輸入、預期輸出、驗證方式、依賴與完成後回寫的核心交付物。未安裝的能力只形成待執行交接，不視為完成。

## 停止、降級與恢復

- 找不到引擎、SDK、必要帳號或建置工具：標記 Blocked。
- 資產來源或授權不明：允許合法暫代資產繼續開發，但不得進入正式 Release Candidate。
- 測試失敗：不得把對應階段標成完成。
- 無法執行的驗證：標記 Unverified，不以靜態閱讀或推測代替執行證據。
- 範圍膨脹：回到 scope cutting，更新 brief、roadmap 與 acceptance matrix。
- 既有專案中途接手：先重建四份核心交付物，再從最早未被證據支持的階段恢復，不強迫重做已驗證成果。
- Agent 或 session 中斷：以下一個未完成且依賴已滿足的 roadmap 項目恢復，不依賴對話記憶。

## 檔案設計

### 新增

- `plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/agents/openai.yaml`
- `plugins/sg-game-dev-skills/skills/ship-small-game/references/stage-gates.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/references/department-routing.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/references/recovery-and-scope-control.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/templates/game-brief.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/templates/delivery-roadmap.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/templates/acceptance-matrix.md`
- `plugins/sg-game-dev-skills/skills/ship-small-game/templates/production-status.md`
- `scripts/check-game-delivery-workflow.py`

### 修改

- `plugins/sg-game-dev-skills/.claude-plugin/plugin.json`
- `plugins/sg-game-dev-skills/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `README.md`
- `docs/CONVENTIONS.md`
- `docs/HANDOFF.md`
- `docs/TOPIC-MAP.md`
- `scripts/hooks/pre-commit`

不修改既有專業 references，不新增職稱型 skills、README、安裝指南或專案 starter。

## Plugin 與版本策略

- `sg-game-dev-skills` 由 `0.26.1` 提升為 `0.27.0`，Claude Code 與 Codex manifests 同步。
- Claude manifest 增加 `./skills/ship-small-game`；Codex manifest 維持指向 `./skills`。
- Claude marketplace 更新 `sg-game-dev-skills` 的使用者可見描述；Codex marketplace schema 不含版本與描述，維持既有內容。
- `agents/openai.yaml` 只提供必要的 display name、short description 與 default prompt。
- 新增內容全部使用相對路徑，不記錄 checkout 絕對路徑。

## Skill TDD 與驗證策略

### RED：無 skill baseline

使用不含 `ship-small-game` 的新 Agent 測試三個情境：

1. 模糊的新 Unity 小遊戲需求。
2. 已做到一半、文件不足的既有遊戲。
3. 缺少資產授權或 Build 工具的受阻專案。

記錄 Agent 是否直接開始寫程式、缺少重大決策閘門、沒有跨部門驗收，或把無法執行的項目視為完成。

### RED：靜態契約

先建立 `scripts/check-game-delivery-workflow.py`，並確認它在實作前因下列缺口失敗：

- skill、三份 references 或四份 templates 不存在。
- 七個階段、混合自主、部門路由或三態證據契約缺失。
- Claude manifest 未列出 workflow。
- 兩份 plugin manifests 未同步為 `0.27.0`。
- workflow 內容包含目前 checkout 的絕對路徑。

### GREEN

只加入能關閉 baseline 失敗與靜態契約缺口的最小內容。完成後以相同三個情境 forward-test，確認 Agent：

- 先盤點再實作。
- 對重大決策停在核准閘門。
- 建立四份核心交付物。
- 依能力路由工作，而不是重寫所有專業知識。
- 不把 Blocked 或 Unverified 宣告成完成。

### 完整驗證

```bash
python3 scripts/check-game-delivery-workflow.py
python3 scripts/check-ui-workflows.py
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
```

另外驗證：

- `ship-small-game` 通過 `quick_validate.py`。
- Claude manifest 包含原本五個 hubs 與新增 workflow，共六個 entries。
- Codex 隔離安裝可發現 workflow、三份 references 與四份 templates。
- description 符合專案長度限制並能從「做完整遊戲」「從構想到 Build」「接手未完成遊戲」等使用者語句觸發。
- repository 追蹤內容沒有 checkout 絕對路徑。
- feature branch 最終乾淨、成功 push，既有 PR 更新到最新 commit。

## 成功標準

- 使用者提出模糊的小型遊戲構想時，Agent 先建立 Game Contract，不直接展開整個專案。
- 使用者核准重大決策後，Agent 能按依賴把工作交給既有企畫、架構、內容、Unity、UI、測試與 Build 能力。
- 中途接手時，Agent 能以證據重建進度並從正確階段恢復。
- 缺少工具、資產授權或 Build 能力時，Agent 明確標記 Blocked 或 Unverified，並提供最小解阻路徑。
- 最終只有在完整流程、測試與 Release Candidate Build 都有證據時，才宣告小型遊戲完成。
- Claude Code 與 Codex plugin 均能安裝並發現新 workflow。
