# 部門路由

以目前階段、已安裝能力、roadmap 依賴與證據狀態，選擇下一個可執行的專業交接。`game-*` hubs 是設計與生產知識來源；總控只界定交接範圍、驗證與狀態，不重寫各 hub 的專業內容。

| 工作 | 主要能力 |
|---|---|
| 核心玩法、GDD、關卡與人工玩測 | `game-design` |
| 系統、資料、AI 與網路架構 | `game-architecture` |
| 美術、音效、動畫、內容與里程碑 | `game-production` |
| 除錯、效能方法與遙測 | `game-tooling` |
| Unity C#、資產、Editor 與自動測試 | `unity-scripting` |
| Unity UI、物理、動畫、Shader 與音效 | `unity-runtime` |
| Unity 效能與 Build | `unity-optimization` |
| UI 證據與規格 | `reference-to-ui-spec` |
| UI 實作 | `build-ui-from-spec` |
| UI 視覺回歸 | `visual-ui-qa` |

只有偵測到 Unity 專案且對應 Unity capability 可用時，才執行 Unity 交接。UI 一律依 `reference-to-ui-spec` → `build-ui-from-spec` → `visual-ui-qa` 順序交接；前一步的輸出是下一步的輸入。

## Handoff Contract

每次 handoff 都使用下列欄位，讓接手者能在不依賴對話記憶的情況下執行與回寫：

- Input：
- Expected output：
- Dependencies：
- Verification：
- Core artifacts to update：

未安裝、不可存取或尚未滿足依賴的 capability，只形成待執行 handoff；它不代表產出、驗證或工作已完成。將缺口和下一個最小解阻步驟記入 roadmap 與 production status，並在 acceptance matrix 保留正確證據狀態。
