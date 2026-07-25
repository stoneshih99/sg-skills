# 2D 排序與 Isometric Tilemap

視角/格子/排序的選型與數學（top-down vs iso vs 2.5D、座標三空間、y-sort 規則）在 **sg-game-dev-skills** 的 algo-2d-projection-and-grids——這篇是 Unity 落地：**sorting 決策鏈怎麼設、Isometric Tilemap 怎麼配、像素完美怎麼保**。

## Sorting 決策鏈：三層，別混用

Unity 2D 的繪製順序由三層決定，優先序固定：

```
Sorting Layer（大分段：Background < World < Effects < UI）
  > Order in Layer（同分段內的顯式順序）
    > Transparency Sort（同層同 order 才輪到：預設比 z，可改軸）
```

- **y-sort 的開關在第三層**：Project Settings → Graphics → Transparency Sort Mode = **Custom Axis**，軸設 `(0, 1, 0)`——y 越小畫越後（越靠前）。這是全專案設定，第一天定。
- **世界物件全交給 y-sort，Order in Layer 只留給規則性分段**（影子 -1、本體 0、頭頂特效 +1）——到處手填 sortingOrder 常數就是 game-dev 那篇說的「逐個手調 z 救火」，每加一個物件壞一次。
- **z 位移與 sort axis 別混用**：用了 custom axis 還有人改 transform.z 排序，兩套規則互相蓋——選一套，2D 專案鎖 y。

## SortingGroup：組合角色的一體排序

多 sprite 組成的角色（身體/武器/裝備分件）掛 **SortingGroup**：對外整組當一個排序單位（group 的 y 參與 y-sort），對內用各 renderer 的 Order in Layer 固定局部順序——沒有它，武器會插進旁邊角色的身體。

```csharp
// 角色根物件：SortingGroup（sortingLayer=World）
// 子件 Order in Layer：影子 -1、身體 0、武器 1、頭頂條 2
// pivot 統一在腳底——y-sort 的基準是接地點（資產規格，進匯入驗收）
```

## Isometric Tilemap 設定組合

| 設定 | 選什麼 | 為什麼 |
|------|--------|--------|
| Grid type | **Isometric** 或 **Isometric Z as Y** | 有 elevation（tile 疊高）才用 Z as Y |
| Z as Y 的 sort axis | Custom Axis `(0, 1, -0.26)` | z 抬高的 tile 要參與 y 排序，-0.26 ≈ tile 高比補償 |
| Tilemap Renderer Mode | **Individual**（角色會走進地圖）/ Chunk（純背景層） | Individual 逐 tile 排序，角色才能與 tile 正確穿插；Chunk 整片合批、效能好但整體一個排序 |
| 分層 | 地面 Chunk + 遮擋物 Individual，各自 Sorting Layer | 地面永遠在下不需要逐 tile 付費——只有會遮擋角色的那層用 Individual |

- **Individual mode 是效能換正確**：逐 tile 打斷合批——遮擋層 tile 數要控制，其餘全走 Chunk（draw call 分析見 `../../unity-optimization/references/perf-rendering.md`）。
- **Tile 資產是 2:1 尺寸**（規格見 game-dev 那篇與 art-asset-types）；Grid 的 cell size 對應 world 單位，邏輯座標用 `Grid.WorldToCell`/`CellToWorld` 換——**遊戲邏輯住 cell/world 空間**，別在螢幕座標算。

## 像素完美（Pixel Perfect）

- 全專案 **PPU 一致**（sprite、tile 同一個 Pixels Per Unit）——混用 PPU 是像素比例錯亂的唯一來源。
- **Pixel Perfect Camera**（URP 內建）：Reference Resolution 定基準解析度、Snap 讓相機與物件貼像素格——手寫取整遲早漏。
- sprite 匯入：Filter Mode = Point、Compression = None（像素風），匯入自動化用 AssetPostprocessor 鎖規格（見 **sg-unity-dev-skills** unity-scripting 的 asset-import-pipeline）。

## 2.5D 的話，這篇大半不用

選了 3D 正交相機路線（岔路裁決見 game-dev 那篇）：不透明 3D 幾何走 z-buffer，**沒有排序問題**；只有掛在 3D 場景裡的 2D sprite（billboard、特效）仍吃 Transparency Sort。別在 2.5D 專案裡重建 y-sort 全家桶。

## 常見坑

- **忘了設 Custom Axis**：預設按 z 排，y-sort 完全沒生效——症狀是角色永遠蓋在建築上。
- **sortingOrder 手填成災**：集中成常數表 + 世界物件一律交 y-sort。
- **遮擋層用 Chunk mode**：角色走到樹後面還蓋在樹上——會遮擋的層換 Individual。
- **pivot 不在腳底**：y-sort 基準錯，高物件排序抖動——匯入規格統一，不是逐個修。
- **Z as Y 沒配 -0.26 軸**：疊高的 tile 排序錯亂。
- **PPU 混用**：某批資產放大 2 倍還帶模糊——匯入管線鎖 PPU + Point filter。
