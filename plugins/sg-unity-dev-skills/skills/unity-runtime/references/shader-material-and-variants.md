# Material 與 Shader Variant

Shader 寫好了，兩個坑會咬人：執行期改 material 破壞合批（DrawCall 爆），以及 shader variant 爆炸（build 時間/記憶體/包體暴增）。這篇是這兩個效能坑。

## MaterialPropertyBlock：改屬性不破合批

**執行期 `renderer.material` = 複製一份 material 實例**——每個實例是獨立 material，打斷合批（見 `../../unity-optimization/references/perf-rendering.md` 的合批天敵是材質切換），且要記得銷毀（記憶體）：

```csharp
// 錯：renderer.material 複製實例、破合批、要清理
renderer.material.color = Color.red;

// 對：MaterialPropertyBlock 改屬性，不複製 material、不破合批
static readonly int s_Color = Shader.PropertyToID("_BaseColor");
MaterialPropertyBlock _mpb;
void SetColor(Color c)
{
    _mpb ??= new MaterialPropertyBlock();
    _renderer.GetPropertyBlock(_mpb);
    _mpb.SetColor(s_Color, c);
    _renderer.SetPropertyBlock(_mpb);   // per-renderer override，合批仍成立（GPU Instancing 友善）
}
```

- **per-instance 的屬性變化用 MaterialPropertyBlock**（受擊閃白、每個敵人不同色）——大量物件改屬性不破合批、無記憶體洩漏。
- **`sharedMaterial` vs `material`**：讀共享設定用 `sharedMaterial`（不複製）；真的要一個獨立 material 才用 `material`（且記得它複製了）。
- **PropertyToID 快取**：`Shader.PropertyToID("_BaseColor")` 快取成 static int，別每次傳字串（字串查找 + GC，見 `../../unity-optimization/references/perf-gc-and-memory.md`）。

## Shader Variant 爆炸

Shader 的 `#pragma multi_compile` / keyword 會為**每個 keyword 組合**生成一個變體——keyword 指數成長：

- **5 個 multi_compile keyword = 2^5 = 32 變體**，每個都要編譯、佔記憶體、進包——**variant 爆炸**讓 build 時間暴增、shader 記憶體膨脹、包體變大。
- **`shader_feature` vs `multi_compile`**：
  - `shader_feature`：**沒被材質用到的變體會被剝離**（build 時只留實際用到的）——適合材質開關。
  - `multi_compile`：**全部保留**（執行期程式碼可切）——只給真的要執行期切換的。
- **診斷**：Shader 的 variant 數在 inspector 可看；Graphics Settings 的 Shader Stripping 控制剝離。

## Shader Stripping（剝離未用變體）

跟 IL2CPP 的 code stripping 同精神（見 `../../unity-optimization/references/build-il2cpp.md`）——build 時剝掉沒用到的變體省資源：

- **Graphics Settings** 的 stripping 設定 + **Shader Variant Collection**（記錄實際用到的變體，預熱 + 保留）。
- **坑：動態用到的變體被剝**：執行期才決定的 keyword 組合，靜態分析看不出被用 → 被剝 → 執行期粉紅或效果消失（同 IL2CPP stripping 坑）——用 Variant Collection 保留、或 `[always included shaders]`。
- **shader 預熱（warmup）**：首次用某變體會即時編譯造成卡頓（見 game-dev perf-common-hotspots 的首次使用成本）——載入畫面 `ShaderVariantCollection.WarmUp()` 預熱。

## 常見坑

- **`renderer.material` 執行期改**：複製實例、破合批、記憶體洩漏——per-instance 用 MaterialPropertyBlock。
- **每次傳字串屬性名**：GC + 查找——`PropertyToID` 快取 static int。
- **multi_compile 濫用**：variant 爆炸、build 慢、包大——材質開關用 shader_feature（可剝離）。
- **動態變體被 stripping 剝掉**：執行期粉紅/效果消失——Variant Collection 保留。
- **首次用變體卡頓**：即時編譯——載入期 WarmUp 預熱。
