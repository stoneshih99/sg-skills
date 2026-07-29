# Custom Inspector 與 PropertyDrawer

編輯器擴充的第一課：**先問值不值得**——每個 Custom Inspector 都是要維護的 Editor 程式碼，且 Editor API 版本間會變。先用內建屬性，撐不住再自訂。

## 先試不寫程式的做法

自訂 Inspector 前，這些 attribute 常常就夠了：

- `[SerializeField] private`：曝露私有欄位（保持封裝，見使用者 CLAUDE.md 的命名規約）。
- `[Range(min,max)]`、`[Tooltip]`、`[Header]`、`[Space]`：分組與約束，零程式碼。
- `[HideInInspector]`、`[ShowIf]`（第三方如 NaughtyAttributes/Odin）：條件顯示。
- `[CreateAssetMenu]`：SO 的建立選單（見 `asset-scriptableobject.md`）。

**能用 attribute 解決就別寫 Custom Inspector**——維護成本差一個量級。

## Custom Inspector vs PropertyDrawer（選型）

| | Custom Inspector（`Editor`） | PropertyDrawer |
|--|------------------------------|----------------|
| 作用範圍 | 整個組件的 Inspector | **單一型別/欄位**的畫法 |
| 適合 | 一個 MonoBehaviour 需要客製整體佈局、按鈕、預覽 | 一個自訂 struct/class 到處出現、要統一畫法 |
| 重用 | 綁一個組件 | **一次寫、所有用到該型別的地方都套** |

**準則**：某個**型別**（如自訂的 `MinMaxRange`）在很多地方出現、要統一畫 → PropertyDrawer（寫一次到處用）；某個**組件**要專屬佈局/工具按鈕 → Custom Inspector。

```csharp
// PropertyDrawer：一次寫，所有 MinMaxRange 欄位都套
[CustomPropertyDrawer(typeof(MinMaxRange))]
public class MinMaxRangeDrawer : PropertyDrawer
{
    public override void OnGUI(Rect r, SerializedProperty prop, GUIContent label)
    { /* 畫雙滑桿 */ }
}
```

## 紀律

- **用 SerializedProperty，不直接改物件**：透過 `serializedObject.FindProperty` + `ApplyModifiedProperties` 修改——才有 Undo、multi-object 編輯、dirty 標記、prefab override。直接改 `target` 欄位會失去這些且不存檔。
- **UIToolkit vs IMGUI**：新 Editor UI 官方推 UI Toolkit（`CreateInspectorGUI`）；IMGUI（`OnInspectorGUI`）仍普遍且範例多。新專案評估 UI Toolkit，但 IMGUI 對小工具更快上手。
- **Editor 程式碼放 `Editor/` 資料夾**：`UnityEditor` 命名空間的東西**不能進建置**——放 `Editor/` 資料夾或用 `#if UNITY_EDITOR` 包起來，否則建置失敗。

## 常見坑

- **為了小事寫 Custom Inspector**：一個 Range 用 `[Range]` 就好，別開 Editor 檔。
- **直接改 target 不走 SerializedProperty**：沒 Undo、不存檔、破 prefab override、multi-select 壞掉。
- **Editor 程式碼沒隔離**：`UnityEditor` 進了執行期組件 → 建置報錯。放 Editor/ 或 `#if UNITY_EDITOR`。
- **硬編 GUI 座標**：Inspector 寬度會變——用 layout（`EditorGUILayout`）或 UI Toolkit 的彈性佈局。
- **過度客製**：整個專案的 Inspector 都魔改，換 Unity 版本一片紅——客製留給真正有價值的，其餘用內建。
