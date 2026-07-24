# 資產匯入管線（AssetPostprocessor）

匯入設定該用程式碼自動化，不靠每個人手點 Inspector（手點必然不一致，見 game-dev content-asset-conventions 的匯入自動化）。這篇是 AssetPostprocessor 的用法與一個會讓你 debug 半天的坑。

## AssetPostprocessor：匯入即套規則

資產進專案時自動套設定——按路徑/類型分流，規則寫在程式：

```csharp
public class TextureImportSettings : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        var importer = (TextureImporter)assetImporter;
        if (assetPath.Contains("/Sprites/"))
        {
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;   // ← 關鍵，見下方坑
            importer.mipmapEnabled = false;
            importer.filterMode = FilterMode.Point;                // 像素風
        }
        if (assetPath.Contains("/UI/"))
            importer.spritePackingTag = "ui";                      // 圖集
    }
}
```

- **按路徑分流**：`assetPath` 對應 game-dev content-asset-conventions 的目錄結構——`/Sprites/`、`/UI/`、`/Audio/` 各套各的規則。
- **對應規格表**：壓縮格式、尺寸上限、mipmap 依平台與用途（見 game-dev art-tech-specs 的 texel density 與壓縮紀律）——匯入器套的就是那些規格。

## 坑：設 textureType=Sprite 不會自動設 spriteImportMode

**這是最容易 debug 半天的一個**：

用 AssetPostprocessor 以程式設 `textureType = TextureImporterType.Sprite`，**不會**像編輯器 GUI 那樣自動幫你把 `spriteImportMode` 設成 `Single`——貼圖會落在 **Multiple 且無切片**，於是 `AssetDatabase.LoadAssetAsset<Sprite>(path)` 永遠拿到 **null**，且沒有任何錯誤訊息。

**解法**：設 `textureType = Sprite` 時，**務必同時明確設** `spriteImportMode`：
- 單張 sprite → `SpriteImportMode.Single`
- 圖集/切片 → `SpriteImportMode.Multiple` 並提供切片資料（`spritesheet` / SpriteEditorDataProvider）

編輯器 GUI 幫你做的隱含步驟，程式碼裡不會自動發生——**凡是 GUI 一鍵搞定的匯入設定，用程式碼時都要懷疑「有沒有隱含步驟沒被觸發」**。

## 驗證與批次

- **匯入驗證**：AssetPostprocessor 裡順手檢查命名/尺寸是否合規（見 game-dev content-asset-conventions 的腳本化驗收）——不合規 `Debug.LogError` 標紅，比人工抽查可靠。
- **既有資產重匯**：改了規則後，既有資產不會自動重跑——`Reimport` 或 `AssetDatabase.ImportAsset` 批次重匯。
- **`OnPostprocessAllAssets`**：一批資產匯入/移動/刪除後的總回呼，適合建索引、更新清單。

## 常見坑

- **spriteImportMode 沒明設**（上面的核心坑）：LoadAsset<Sprite> 拿到 null 且無報錯。
- **假設 GUI 的隱含行為**：程式設匯入器少了 GUI 幫你做的步驟——每個設定都明確寫。
- **規則改了沒重匯既有資產**：新資產對、舊資產還是舊設定——改規則要批次重匯。
- **匯入器沒按路徑分流**：全部資產套同一規則，UI 圖被當一般貼圖壓——用 assetPath 分流。
- **手點 Inspector 當標準**：某人手調的設定活在他的機器，換人/重匯就失傳——設定進 AssetPostprocessor 程式碼。
