---
name: unity-scripting
description: Unity 寫程式與資產的實作決策與坑——五家族：腳本（生命週期/執行順序、UniTask vs Coroutine、GetComponent 快取、Camera.main 坑）、輸入（新 Input System vs 舊、Action Maps、輸入→意圖分層、重綁鍵、input buffer）、資產（ScriptableObject vs JSON、Addressables、AssetPostprocessor）、測試（EditMode vs PlayMode、可測性）、編輯器擴充（Custom Inspector、EditorWindow/Gizmos）。當在 Unity 寫遊戲邏輯、處理輸入、設計資產、寫測試或做編輯器工具時使用。執行期系統（物理/動畫/音訊/UI）見 unity-runtime、效能與建置見 unity-optimization、引擎中立架構見 sg-game-dev-skills。含 C#。
---

# Unity 寫程式與資產（Unity Scripting）

> **定位**：Unity **寫 code 與資產**這一面的實作決策與坑。執行期表現系統（物理/動畫/音訊/UI）見 `unity-runtime`；效能與建置見 `unity-optimization`；引擎中立架構見 **sg-game-dev-skills**。只收 Unity 專屬決策/坑，不收 API 教學。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 寫遊戲邏輯：生命週期、非同步、組件通訊 | 腳本 | ↓ Script |
| 處理輸入：Input System、Action Maps、意圖分層、重綁 | 輸入 | ↓ Input |
| 資料與資產：ScriptableObject、載入、匯入、序列化 | 資產 | ↓ Asset |
| 寫測試、可測性 | 測試 | ↓ Test |
| 做編輯器工具：Inspector、視窗、Gizmos | 編輯器 | ↓ Editor |

貫穿原則：**Unity 的「方便寫法」常有隱藏成本**（`Camera.main`、每幀 `GetComponent`、`Update` 裡配置）——選型時把 Unity 專屬成本算進去。

## Script（腳本與架構落地）

| 何時 | 讀 |
|------|-----|
| 生命週期與執行順序、取用時機、Camera.main 多場景坑 | `references/script-lifecycle-execution.md` |
| 非同步：Coroutine vs UniTask vs Awaitable、取消與生命週期 | `references/script-async.md` |
| 服務定位 vs singleton、組件通訊、GetComponent 快取 | `references/script-architecture-glue.md` |

## Input（輸入）

| 何時 | 讀 |
|------|-----|
| 新 Input System vs 舊、Action Asset/Maps、三種讀取方式、Enable 坑 | `references/input-system-setup.md` |
| 輸入→意圖分層(system-3c 落地)、重綁鍵、input buffer/coyote 容錯 | `references/input-architecture.md` |

## Asset（資料與資產）

| 何時 | 讀 |
|------|-----|
| ScriptableObject 當資料/config/事件、vs JSON、執行期污染坑 | `references/asset-scriptableobject.md` |
| AssetPostprocessor 自動化匯入、spriteImportMode 坑 | `references/asset-import-pipeline.md` |
| 載入策略：Addressables vs Resources vs 直接參照 | `references/asset-loading.md` |

## Test（測試）

| 何時 | 讀 |
|------|-----|
| EditMode vs PlayMode 選型、Unity Test Framework、asmdef、測跨幀 | `references/test-framework.md` |
| 可測性設計：純邏輯抽離 MonoBehaviour、依賴注入、mock Unity 依賴 | `references/test-testability.md` |

## Editor（編輯器擴充）

| 何時 | 讀 |
|------|-----|
| Custom Inspector / PropertyDrawer 何時值得、怎麼做 | `references/editor-custom-inspector.md` |
| EditorWindow、Gizmos 除錯繪製、選單工具 | `references/editor-tools.md` |
