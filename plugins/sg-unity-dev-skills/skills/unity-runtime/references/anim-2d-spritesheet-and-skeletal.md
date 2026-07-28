# 2D 角色動畫落地：Spritesheet / Unity 2D Animation / Spine

逐幀 vs 骨骼的選型（成本曲線、朝向乘數、混搭規矩）在 **sg-game-dev-skills** 的 anim-2d-frames-vs-skeletal——這篇是 Unity 落地：**逐幀怎麼組、骨骼用哪套 runtime、各自的坑**。

## 逐幀路線：Spritesheet 進 Unity

- **匯入**：Sprite Mode = Multiple → Sprite Editor 切割（規則圖集用 Grid By Cell Size）；pivot 統一腳底、PPU 全專案一致（規格自動化用 AssetPostprocessor，見 **sg-unity-dev-skills** unity-scripting 的 asset-import-pipeline——切割參數手調 30 張圖必出錯）。
- **播放方式二選一**：

| 方式 | 適合 | 代價 |
|------|------|------|
| **AnimationClip + Animator** | 需要狀態機、轉移、動畫事件的角色 | 每個 Animator 有常駐開銷 |
| **程式換幀**（自己排程換 `SpriteRenderer.sprite`） | 大量簡單循環（金幣、火把、環境動效） | 自己管計時，但零 Animator 開銷 |

**別為每個小東西開 Animator**——幾百個場景動效各掛一個 Animator 是經典效能債；簡單循環用一個集中管理器換幀。

- **SpriteAtlas 必開**：散圖不打包，draw call 隨動畫幀數飛（合批分析見 `../../unity-optimization/references/perf-rendering.md`）。
- **判定幀掛 Animation Event**：攻擊第 N 幀出 hitbox、第 M 幀可取消——事件驅動邏輯，不要用「播了 0.3 秒」估。

## 骨骼路線：三套 runtime 選型

| 方案 | 是什麼 | 選它當 | 痛點 |
|------|--------|--------|------|
| **Unity 2D Animation**（官方 package） | PSD Importer 拆件、內建綁骨/蒙皮/IK、Sprite Library 換裝 | 自己動手、預算敏感、中等複雜度 | 工具鏈比 Spine 陽春（曲線編輯、混合層級） |
| **Spine** | 專業 2D 骨骼工具＋官方 Unity runtime | 美術/外包生態成熟、換裝混合需求重 | **editor 按席位收費**、runtime 版本綁定、學習成本 |
| **DragonBones** | 免費 Spine 類 | 預算為零且能接受 | 生態與維護弱，長線專案風險 |

**裁決**：外包或合作美術已在 Spine 生態 → Spine（別逼美術換工具）；一人全包＋想省授權費 → Unity 2D Animation 夠用到中等複雜度。**先用動作清單試做一個最複雜的角色再定案**——切換 runtime 的成本是全部動畫資產。

## Spine-Unity 整合的坑（選了 Spine 才讀）

- **SkeletonAnimation vs SkeletonMecanim**：前者 Spine 自驅（API 直控、混合強、Spine 原生功能全開）；後者包進 Animator（跟 Unity 狀態機/Timeline 整合順）。預設 **SkeletonAnimation**——除非動畫全隊都活在 Animator 工作流裡。
- **runtime 版本與 editor 版本嚴格配對**：4.1 的匯出檔配 4.2 runtime 會壞——版本寫進專案 README 與外包交付規格。
- **一個 skeleton 一個材質**：角色多時 draw call 注意；換裝混圖集會破合批。
- **縮放坑**：匯入 scale 與 PPU 的組合影響物理/位移數值——進專案第一天定，後改全部動畫數值飄。

## Unity 2D Animation 的坑（選了官方才讀）

- **Sprite Skin 是 CPU 成本**：蒙皮頂點每幀算——大量骨骼角色開 Burst/collections 加速選項，數量多時進 profiler 看（`../../unity-optimization/references/perf-profiling.md`）。
- **換裝走 Sprite Library / SpriteResolver**：換 Library Asset 換整套皮，不要 runtime 改 SpriteRenderer 逐件換。
- **PSD Importer 的圖層紀律**：圖層名=件名、不合併、pivot 規範——美術端的檔案規矩，進交付規格。

## 常見坑

- **每個場景動效掛 Animator**：集中換幀管理器。
- **散圖不進 SpriteAtlas**：draw call 飛。
- **Spine 版本不配對**：匯出檔打不開或動作行為變。
- **pivot/PPU 不統一**：y-sort 抖、縮放飄（與 2d-sorting-and-isometric.md 同一條資產紀律）。
- **用時間估判定幀**：變速（加速 buff、頓幀）就錯——Animation Event / Spine Event 驅動。
- **選 runtime 沒試最複雜角色**：中途換路線=動畫資產全重做。
