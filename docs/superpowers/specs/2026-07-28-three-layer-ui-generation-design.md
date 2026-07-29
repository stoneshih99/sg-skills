# 三層 UI 生成 Workflow Skills 設計

## 目標

在 `sg-dev-skills` 新增三個可獨立觸發、也可依序串接的 workflow skills，把 UI 工作拆成：

1. 視覺參考轉 UI 規格。
2. UI 規格轉可執行介面。
3. 實作結果做視覺與互動驗收。

三層共用平台中立的輸入／輸出契約。Codex、Claude Code 與不同前端或遊戲引擎只替換執行工具，不複製核心流程。

## 範圍

### 本次包含

- `reference-to-ui-spec`
- `build-ui-from-spec`
- `visual-ui-qa`
- 每個 skill 一份對應輸出模板
- Claude Code 與 Codex plugin manifest 更新
- `docs/TOPIC-MAP.md`、`docs/CONVENTIONS.md` 與根 README 路由說明
- `sg-dev-skills` 雙 manifest 同步版本提升
- skill 使用情境、連結、manifest 與雙 plugin 相容性驗證

### 本次不包含

- 自製 UI 生成模型、影像辨識模型或向量資料庫
- 綁定單一 UI framework 的 starter project
- 複製 Sites、Playwright、Unity、Figma 或其他工具的基礎文件
- 自動部署；只有使用者要求交付或部署時才進入相應平台流程
- 將既有 UI/UX 決策 references 搬進新 skills

## Plugin 歸屬

三個 skills 放在 `plugins/sg-dev-skills/skills/`。

理由：

- 從參考、規格、實作到驗收是通用工程 workflow，不限遊戲或 Unity。
- `sg-game-dev-skills` 繼續擁有引擎中立的遊戲 UI/UX 決策與規格知識。
- `sg-unity-dev-skills` 繼續擁有 uGUI、UI Toolkit、Canvas 與 Unity API 的具體實作。
- workflow 遇到遊戲或 Unity 專屬決策時，只以 skill 名稱要求載入相鄰 plugin，不建立跨 plugin 相對連結。

三個 workflow 的觸發語意不同，因此維持獨立 skill。若未來 UI workflow 超過 4 個，再評估合併成 `ui-generation` hub。

## 三層契約

### 1. `reference-to-ui-spec`

**觸發情境**

- 使用者提供截圖、影片、網站、HTML 或設計參考，希望分析、重製或轉成 UI brief。
- 現有需求只有「現代、漂亮、像某網站」等模糊描述，需要先收斂成可驗證規格。

**輸入**

- 一個或多個可存取的視覺／程式參考。
- 目標使用者、介面目的與目標平台；缺少時只詢問會改變整體方向的資訊。
- 原創邊界：精確重製、自有產品延伸或只借用高階視覺語法。

**流程邊界**

- 有 HTML/CSS/JS 時以原始行為為準。
- 有影片時擷取能代表狀態變化的關鍵畫面；工具依當前 runtime 能力選擇。
- 把觀察與推論分開，不從靜態截圖宣稱精確動畫技術。
- 規格描述資訊層級、layout、type、color、assets、states、motion、responsive、accessibility、performance 與禁止事項。

**輸出**

- 依 `templates/ui-spec.md` 產生一份 UI 規格。
- 所有未知資訊明確標成假設或待補資料。
- 規格完整到下一層不必重新觀看原始參考，也能開始實作；原始資產仍需保留來源與使用邊界。

### 2. `build-ui-from-spec`

**觸發情境**

- 使用者已有 UI spec、wireframe、設計 brief 或可直接實作的頁面需求。
- 使用者要求建立或修改 HTML、React、其他前端 UI，或要求把同一規格落到 Unity UI。

**輸入**

- UI spec；若沒有，先要求使用 `reference-to-ui-spec` 或建立最小等價 brief。
- 目標 repository、既有技術棧與交付形式。
- 是否需要本機預覽、artifact、部署或只修改原始碼。

**流程邊界**

- 先讀既有 design system、components 與 project instructions，優先重用。
- 選擇當前 runtime 可用的執行工具：
  - Codex 網站工作可使用 Sites。
  - 一般前端專案使用既有 stack 與瀏覽器／測試工具。
  - Unity UI 載入 `unity-expert`／`sg-unity-dev-skills` 的對應知識後在實際專案落地。
- 實作內容、資料與互動狀態，不只畫靜態外觀。
- 未經要求不部署、不替換品牌資產、不擴張成多頁應用。

**輸出**

- 依 `templates/ui-build-brief.md` 固定實作邊界與驗收條件。
- 可執行 UI、必要資產與最小驗證結果。
- 清楚列出尚未驗證或因環境缺失無法完成的項目。

### 3. `visual-ui-qa`

**觸發情境**

- UI 已完成，需要比對規格、截圖或參考設計。
- 發生跑版、響應式、鍵盤操作、互動狀態或視覺回歸問題。

**輸入**

- 可執行 UI 或可開啟的 build。
- UI spec／驗收基準；若只有參考圖，先定義可比較與不可推斷的範圍。
- 必測 viewport、平台、互動路徑與可接受差異。

**流程邊界**

- 先驗證頁面能載入且 console 沒有阻斷錯誤。
- 依指定 viewport 擷取證據，至少檢查 layout、typography、color、assets、states 與 overflow。
- 驗證 keyboard、focus、loading、empty、error、reduced motion，以及需求指定的互動。
- 將問題分成規格不符、實作缺陷、參考資訊不足及主觀偏好。
- QA 預設只診斷與報告；只有使用者同時要求修正時才修改實作。

**輸出**

- 依 `templates/ui-qa-report.md` 產生附證據的 QA 報告。
- 每項問題包含嚴重度、重現條件、預期、實際與最小修正方向。
- 不用「看起來差不多」取代可重複驗證。

## 串接資料流

```text
視覺參考／模糊需求
        ↓
reference-to-ui-spec
        ↓ ui-spec.md
build-ui-from-spec
        ↓ 可執行 UI + build evidence
visual-ui-qa
        ↓ ui-qa-report.md
修正後重新執行 visual-ui-qa
```

每一層只依賴上一層的輸出契約，不依賴上一層使用的特定工具。使用者已有合格輸入時，可以直接從第二或第三層開始。

## 平台相容策略

- `SKILL.md` 不寫死 Codex 或 Claude Code 專有命令。
- 需要工具時先檢查當前 runtime 已提供的能力，再選 Sites、瀏覽器、Playwright、現有測試或 Unity 工具。
- Codex 與 Claude Code 共用同一個 skill 目錄；不建立兩份內容副本。
- Claude manifest 分別列出三個 skill 路徑；Codex manifest 繼續指向整個 `./skills`。
- 不在 canonical skill 中承諾未安裝的 plugin 或外部服務一定存在。

## 失敗與停止條件

- 參考無法存取：列出缺少的確切檔案或 URL，不虛構畫面內容。
- 規格存在會改變架構的矛盾：停止實作並提出單一阻斷問題。
- 執行環境無法啟動：保留診斷證據，不宣稱完成視覺 QA。
- 缺少原始字型、圖片或品牌資產：使用明確 placeholder，不能暗示已精確重製。
- 無部署授權：完成本機或 artifact 驗證後停止。

## 驗證策略

每個 skill 依序驗證，不能三個一起寫完才測：

1. **RED**：用未載入新 skill 的獨立情境，記錄預設輸出缺少哪些契約欄位。
2. **GREEN**：新增該 skill 後重跑同類情境，確認輸出符合模板與停止條件。
3. **REFACTOR**：只修補實際測試暴露的缺口，再重跑。

三個 skills 都完成後執行：

```bash
python3 scripts/check-links.py
python3 scripts/check-plugin-compat.py
claude plugin validate .
```

另外人工確認：

- 三個 description 的觸發語意沒有互相吞掉。
- 每個 `SKILL.md` 保持精簡，細節只放必要模板。
- `.claude-plugin/plugin.json` 與 `.codex-plugin/plugin.json` 版本一致。
- Git diff 只包含本設計列出的 paths。

## 成功標準

- 使用者能單獨要求「把參考轉規格」、「照規格做 UI」或「驗收這個 UI」，Agent 會選中正確 skill。
- 完整串接時，三層透過文件契約交接，不需要隱藏上下文。
- 同一份 skills 可被 Claude Code 與 Codex plugin 安裝。
- 通用 workflow 沒有重寫 game-dev 或 Unity 專屬 UI 知識。
- 全部 repository validators 通過。
