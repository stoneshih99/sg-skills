# ScriptableObject：資料 / config / 事件

ScriptableObject（SO）是 Unity 資料驅動的主力——但它有一個玩過的人都踩過的坑（執行期修改污染資產）。這篇是 SO 的三種用法、vs JSON 的選型、和那個坑。

## SO 的三種角色

1. **資料容器 / config**：技能表、道具、敵人設定——一個 asset 一筆或一組資料。這是 game-dev「內容即資料」（data-config-driven）在 Unity 的落地。
2. **共享狀態容器**：多個系統引用同一個 SO 讀寫共享值（謹慎用，見下方坑）。
3. **事件通道**：SO 當解耦的全域事件匯流排（發送者與接收者都只引用 SO asset，互不認識）。

```csharp
[CreateAssetMenu(menuName = "Config/Skill")]
public class SkillData : ScriptableObject
{
    public string id;
    public float baseDamage;
    public float cooldown;
    public SkillData[] combo;      // 用 SO 參照別的 SO——編輯器可拉、可序列化
}
```

## SO vs JSON / 其他 config

| | ScriptableObject | JSON / CSV |
|--|-----------------|-----------|
| 編輯 | Unity 編輯器內、有型別檢查、可拉資產參照 | 外部工具、設計師/試算表友善 |
| 資產參照 | **直接引用其他 SO/prefab/材質** | 只能存 id 字串再解析 |
| 版控 | Unity 序列化檔（YAML），可 merge 但笨重 | 純文字，diff/merge 友善 |
| 執行期熱重載 | 需自寫 | 重讀檔即可 |
| 大量同型列 | 一列一 asset 會爆檔案數 | 一張表搞定 |

**選型**：需要**引用其他 Unity 資產**（技能連特效 prefab、道具連圖示）→ SO；**大量同型列 + 設計師用試算表調** → JSON/CSV 匯入（或 SO 但用一個容器 SO 裝陣列）；跨引擎/後端共用資料 → JSON。混合常見：主結構 SO、大批數值從 CSV 匯入生成 SO。

## 坑：執行期修改 SO = 污染資產

**SO 是資產，不是實例**——執行期改了 SO 的欄位，改的是**磁碟上那份資產**：

- 編輯器裡：改動會**留在資產上**，退出 Play Mode 不還原——你的 config 被玩測「改壞」且進了版控。
- 建置版：SO 修改不持久（無資產可寫），但**同一 SO 被多個物件共享**時，一個改了全部看到——「敵人 A 中毒，敵人 B 也顯示中毒」這種靈異。

**解法**：
- SO 當**唯讀資料源**：執行期只讀不寫。
- 需要每個實例有自己的可變狀態 → 執行期把 SO 的值**拷貝到運行時物件**（MonoBehaviour 欄位或 plain class），改拷貝不改 SO（對應 game-dev system-skill 的「基礎值 vs 運行時狀態」——SO 是基礎值）。
- 真的需要共享可變狀態（如全域遊戲進度）→ 明確設計成「Runtime SO」並清楚它是刻意共享，且建置版要另存持久化（見 `asset-loading.md` 存檔）。

## SO 事件通道（進階）

```csharp
[CreateAssetMenu(menuName = "Events/GameEvent")]
public class GameEvent : ScriptableObject
{
    readonly List<Action> _listeners = new();
    public void Raise() { for (int i = _listeners.Count-1; i>=0; i--) _listeners[i](); }
    public void Register(Action l) => _listeners.Add(l);
    public void Unregister(Action l) => _listeners.Remove(l);
}
```

- 好處：發送與接收方在 Inspector 各自引用同一 SO，零程式耦合、跨場景可用。
- 坑：**監聽者要在 OnDisable 退訂**——SO 存活整個遊戲，持有已銷毀物件的回呼會洩漏（同 `script-architecture-glue.md`）。
- 派發時機、遞迴防護等**架構原則**見 game-dev system-foundation。

## 常見坑

- **執行期改 SO**：上面的核心坑——SO 唯讀，可變狀態拷到運行時。
- **一個 SO 被多物件共享卻各自要獨立狀態**：忘了拷貝，狀態互相污染。
- **SO 檔案數爆炸**：三百個道具三百個 asset，資料夾與版控難管——用容器 SO 裝陣列，或 CSV 匯入。
- **SO 事件不退訂**：SO 生命週期 = 整個遊戲，洩漏比一般事件更嚴重。
