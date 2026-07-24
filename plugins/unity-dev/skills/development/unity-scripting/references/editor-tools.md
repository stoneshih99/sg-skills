# 編輯器工具：EditorWindow、Gizmos、選單

除錯工具是「加速所有後續開發」的投資（見 game-dev game-tooling）——這篇是那套工具在 Unity 的落地：視覺化除錯用 Gizmos、批次操作用選單、複雜工具用 EditorWindow。

## Gizmos：Unity 的 debug draw

game-dev game-tooling 的 debug-draw（把看不見的變看得見）在 Unity 就是 **Gizmos / Debug.DrawLine**：

```csharp
void OnDrawGizmos()            // 一直畫
void OnDrawGizmosSelected()    // 選中才畫（較省）
{
    Gizmos.color = Color.red;
    Gizmos.DrawWireSphere(transform.position, attackRange);   // 攻擊範圍
    Gizmos.DrawLine(transform.position, target.position);      // 目標線
}
```

- **Scene view 用 Gizmos**（`OnDrawGizmos`）、**執行期跨幀用 `Debug.DrawLine`/`DrawRay`**（可設 duration，Game view 需開 Gizmos）。
- 對應 game-tooling debug-draw 的清單：碰撞範圍、AI 視野扇形與狀態、路徑、生成點、攝影機邊界——照抄那份清單，用 Gizmos 畫。
- **分層開關**：Gizmos 多了會糊——用 static bool / EditorPrefs 分系統開關（對應 debug-draw 的分層），預設關。
- `OnDrawGizmos` 每幀在 Editor 跑且不便宜——別放重運算，畫太多會拖 Scene view。

## 選單工具：批次操作

```csharp
[MenuItem("Tools/Rebake All Enemy Data")]
static void RebakeEnemyData() { /* 批次處理 */ }

[MenuItem("Tools/Validate Assets")]
static void Validate() { /* 掃資產查命名/規格，對應 content-asset-conventions 腳本化驗收 */ }
```

- 一次性/批次的維護操作（重匯資產、驗證、生成 SO from CSV）掛選單，一鍵跑。
- `[MenuItem]` 也能加驗證函式（灰掉不可用時）、快捷鍵。
- **Context Menu**（`[ContextMenu]`）：掛在組件上的右鍵操作，適合「重置這個組件」「測試這個技能」的即時動作。

## EditorWindow：複雜工具

需要持續互動的工具（關卡編輯器、資料總覽、生成器）用 EditorWindow：

- 門檻比選單高——**先問值不值得**（見 `editor-custom-inspector.md` 的同一原則），一次性操作用選單就好。
- 適合：需要狀態、需要瀏覽清單、需要即時預覽的工具。
- UI Toolkit 對複雜 EditorWindow 比 IMGUI 好維護（佈局、資料綁定）。

## 遊戲內除錯工具（vs 編輯器工具）

- **編輯器工具**（本篇）：開發期在 Unity 編輯器裡用。
- **遊戲內除錯**（控制台、作弊指令、時間控制、watch 面板）：在**執行的遊戲裡**用——那是 game-tooling 的 debug-console-and-cheats / debug-time-control，在 Unity 用 IMGUI overlay 或 UI Toolkit 做，發佈版用 `#if` / 編譯符號剝離（見 game-dev debug-console 的發佈版上鎖）。兩者互補。

## 常見坑

- **Editor 程式碼進建置**：`UnityEditor` API 放 `Editor/` 或 `#if UNITY_EDITOR`——否則建置失敗（同 editor-custom-inspector）。
- **OnDrawGizmos 放重運算**：每幀在 Editor 跑，拖慢 Scene view——只畫，不算。
- **Gizmos 全開不分層**：糊成一團——分層開關、預設關（同 game-tooling debug-draw）。
- **為一次性操作寫 EditorWindow**：選單就夠——EditorWindow 留給需要持續互動的。
- **工具寫死路徑/假設**：換專案結構就壞——路徑用常數集中，或掃描而非硬編。
