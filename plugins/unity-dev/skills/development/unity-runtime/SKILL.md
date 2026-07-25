---
name: unity-runtime
description: Unity 執行期表現系統的實作決策與坑——七家族：物理（Rigidbody/碰撞、CCD 穿隧、Raycast NonAlloc、層矩陣）、多人連線（NGO/Mirror/Photon 選型、NetworkVariable vs RPC、ownership/authority）、著色器（Shader Graph vs HLSL、URP/HDRP、MaterialPropertyBlock、variant 爆炸）、動畫（Animator/Mecanim、Has Exit Time 坑、Timeline/Tween 選型）、音訊（AudioMixer、AudioSource 2D/3D、Load Type 記憶體取捨）、UI（uGUI vs UI Toolkit、Canvas rebuild、Raycast Target）、2D（sprite 排序 y-sort、SortingGroup、Isometric Tilemap、Pixel Perfect）。當在 Unity 做物理、多人連線/netcode、著色器、動畫、音訊、介面，或 2D/isometric 排序與 Tilemap 時使用。寫 code/資產見 unity-scripting、效能建置見 unity-optimization、引擎中立設計見 sg-game-dev-skills。含 C#。
---

# Unity 執行期系統（Unity Runtime）

> **定位**：Unity **執行期表現系統**（物理/動畫/音訊/UI）的實作決策與坑。寫 code 與資產見 `unity-scripting`；效能與建置見 `unity-optimization`；引擎中立設計（手感、UI 架構、音效設計）見 **sg-game-dev-skills**。只收 Unity 專屬決策/坑。

**先查域總表，再進家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| 物理：Rigidbody、碰撞、raycast、穿隧 | 物理 | ↓ Physics |
| 多人連線：Netcode 方案選型、NetworkVariable/RPC、authority | 連線 | ↓ Net |
| 寫 shader/材質：Shader Graph、URP/HDRP、variant | 著色器 | ↓ Shader |
| 動畫/演出：Animator、Timeline、Tween | 動畫 | ↓ Anim |
| 音訊：AudioMixer、AudioSource、匯入 | 音訊 | ↓ Audio |
| 介面：uGUI vs UI Toolkit、Canvas 效能 | UI | ↓ UI |
| 2D：sprite 排序、y-sort、Isometric Tilemap、像素完美 | 2D | ↓ 2D |

## Physics（物理）

| 何時 | 讀 |
|------|-----|
| Rigidbody 三身份、FixedUpdate 施力、interpolation、CCD、碰撞 vs 觸發、層矩陣 | `references/physics-rigidbody-and-collision.md` |
| Raycast/Overlap 查詢、NonAlloc 防 GC、LayerMask 剪枝、碰撞效能 | `references/physics-queries-and-performance.md` |

## Shader（著色器與材質）

| 何時 | 讀 |
|------|-----|
| Shader Graph vs 手寫 HLSL、URP/HDRP/Built-in 管線綁定、何時值得自訂 | `references/shader-authoring.md` |
| MaterialPropertyBlock 不破合批、shader variant 爆炸與 stripping、預熱 | `references/shader-material-and-variants.md` |

## Net（多人連線）

| 何時 | 讀 |
|------|-----|
| Unity netcode 方案選型：NGO/Netcode for Entities/Mirror/FishNet/Photon | `references/net-solution-selection.md` |
| NGO 實作：NetworkVariable vs RPC、ownership/authority、NetworkTransform 插值 | `references/net-ngo-patterns.md` |

## Anim（動畫與演出）

| 何時 | 讀 |
|------|-----|
| Animator/Mecanim 狀態機紀律、Layer/Mask、轉移(Has Exit Time 坑)、動畫事件 | `references/anim-mecanim.md` |
| Timeline / Tween / 程式動畫選型、過場 skip 保護、tween 生命週期 | `references/anim-timeline-and-tweens.md` |
| 2D 角色動畫：spritesheet 組裝、Unity 2D Animation vs Spine runtime | `references/anim-2d-spritesheet-and-skeletal.md` |

## Audio（音訊）

| 何時 | 讀 |
|------|-----|
| AudioMixer bus/snapshot/ducking、AudioSource 2D/3D、播放方式、池化 | `references/audio-mixer-and-sources.md` |
| 音訊匯入 Load Type(記憶體 vs CPU)、壓縮格式、voice 上限與效能 | `references/audio-import-and-performance.md` |

## UI

| 何時 | 讀 |
|------|-----|
| uGUI vs UI Toolkit 選型與適用 | `references/ui-toolkit-vs-ugui.md` |
| uGUI 效能：Canvas 分割與 rebuild、Raycast Target 坑 | `references/ui-ugui-performance.md` |

## 2D

| 何時 | 讀 |
|------|-----|
| sorting 決策鏈與 y-sort、SortingGroup、Isometric Tilemap 設定、Pixel Perfect | `references/2d-sorting-and-isometric.md` |
