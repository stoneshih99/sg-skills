---
name: game-production
description: 遊戲生產流程與資產標準的單一知識入口：流程三件——里程碑（prototype→上線的階段門檻、排程估算、驗收）、建置管線（版控/LFS、CI、RC 凍結與發版）、內容量產（黃金樣本、資產規範、外包交接）；資產標準五件——美術（風格指南、技術規格、視覺可讀性）、音訊（音效、互動音樂、混音響度）、動畫特效、本地化（字串外化、多語版面）、UI/UX（HUD 與選單、無障礙、UI 效能）。當「怎麼排時程」「要發版了」「內容做不完」「發外包」「風格不統一」「規格怎麼定」「音量不一致」「特效廉價」「翻譯破版」「HUD 太擠」時使用。引擎中立，偏個人開發與小團隊。
---

# 遊戲生產（Game Production）

> **定位**：本 skill 是「怎麼生產遊戲、產物該長什麼樣」的**領域知識入口**，不是可執行的工作流。與工作流工具（plan mode、spec 類流程）搭配時，作為決策與規格的知識來源。

涵蓋八個域：流程三件（里程碑 / 建置 / 量產）+ 標準五件（美術 / 音訊 / 動畫特效 / 本地化 / UI-UX）。**先查下面的域總表，再進該域的細表挑要讀的 reference。**

## 域總表

| 你的問題 | 域 | 細表 |
|----------|----|------|
| 專案怎麼排階段、時程爆了、驗收怎麼跑 | 里程碑 | ↓ Milestone |
| 版控、出 build、CI、發版、hotfix | 建置管線 | ↓ Build |
| 內容量產、資產命名、外包交接 | 內容量產 | ↓ Content |
| 風格、美術規格、資產類型、畫面可讀性 | 美術標準 | ↓ Art |
| 音效、音樂、混音、音訊實作 | 音訊標準 | ↓ Audio |
| 動作手感的動畫面、特效設計與效能 | 動畫特效 | ↓ Anim/VFX |
| 多語、字串、翻譯、破版 | 本地化 | ↓ Localization |
| HUD、選單、UI 手感、無障礙、UI 效能 | UI/UX | ↓ UI/UX |

通用原則貫穿全部：**黃金樣本先行**（標準是做出來的不是寫出來的）、**規格從實測預算反推**、**驗收清單腳本化**。

## Milestone（里程碑）

| 何時 | 讀 |
|------|-----|
| 定階段目標與驗收門檻（必讀） | `references/milestone-stage-definitions.md` |
| 排時程、估算、buffer、時程爆掉 | `references/milestone-planning-and-estimation.md` |
| 里程碑到期驗收、回顧會 | `references/milestone-review.md` |
| 要寫一頁里程碑計畫 | `templates/milestone-plan.md` |

## Build（建置管線）

| 何時 | 讀 |
|------|-----|
| 專案起步設版控、LFS、場景衝突、分支 | `references/build-version-control.md` |
| 一鍵建置、build 編號、CI、多平台 | `references/build-automation.md` |
| 發版：RC 凍結、回歸清單、平台提交、hotfix | `references/build-release-checklist.md` |

## Content（內容量產）

| 何時 | 讀 |
|------|-----|
| 量產開跑前：黃金樣本、管線、批次思維（必讀） | `references/content-pipeline-setup.md` |
| 目錄結構、命名規則、規格表、驗收清單 | `references/content-asset-conventions.md` |
| 發外包 / 多人分工交接 | `references/content-outsourcing-handoff.md` |

## Art（美術標準）

| 何時 | 讀 |
|------|-----|
| 定視覺方向、風格飄移 | `references/art-style-guide.md` |
| 定技術規格：texel density、圖集、LOD、材質預算 | `references/art-tech-specs.md` |
| sprite / tilemap / UI / 動畫 / 3D 各類製作要點 | `references/art-asset-types.md` |
| 畫面驗收、「看不清楚」 | `references/art-visual-readability.md` |

## Audio（音訊標準）

| 何時 | 讀 |
|------|-----|
| 建音效庫、音效單調 | `references/audio-sfx-design.md` |
| 音樂與遊戲狀態互動、loop | `references/audio-music-interactivity.md` |
| bus 結構、響度、ducking、聲音糊掉 | `references/audio-mixing-loudness.md` |
| 觸發規則、隨機化、3D 衰減、voice 上限 | `references/audio-implementation.md` |

## Anim/VFX（動畫與特效）

| 何時 | 讀 |
|------|-----|
| 角色動作：前搖後搖、狀態機、root motion | `references/anim-game-principles.md` |
| 特效設計：三段結構、形狀、色彩職責 | `references/anim-vfx-design.md` |
| 粒子預算、overdraw、flipbook、pooling | `references/anim-vfx-tech-specs.md` |

## Localization（本地化）

| 何時 | 讀 |
|------|-----|
| 專案起步立字串規矩（必讀） | `references/loc-text-externalization.md` |
| 文字膨脹、字型、偽本地化、破版 | `references/loc-layout-and-fonts.md` |
| 翻譯交接、LQA、文化化 | `references/loc-workflow.md` |

## UI/UX

| 何時 | 讀 |
|------|-----|
| HUD 資訊分級、選單結構 | `references/ui-hud-and-menus.md` |
| UI 回饋、轉場、焦點導航、多輸入適配 | `references/ui-interaction-feel.md` |
| 字級、色弱、重綁鍵、字幕 | `references/ui-accessibility.md` |
| 解析度適配、安全區、UI 效能 | `references/ui-tech-specs.md` |

## 相鄰 skill

- 企畫層（核心循環 / 範圍 / 風險 / 玩測 / 手感）：`../../planning/`
- 程式架構（資料驅動 / 演算法）：`../../architecture/`
- 除錯與效能工具（profiler / debug draw / 遙測）：`../../tools/`
