# 平台差異與條件編譯

多平台 Unity 專案的技術債特別隱蔽：單平台好好的，換平台就崩、效能爆、或某功能沒了。這篇是條件編譯與平台差異的紀律。game-dev build-automation 的多平台原則（最弱平台優先、平台差異集中）是引擎中立，這篇是 Unity 落地。

## 條件編譯：平台專屬程式碼

```csharp
#if UNITY_IOS
    // iOS 專屬（原生插件呼叫、平台 API）
#elif UNITY_ANDROID
    // Android 專屬
#elif UNITY_STANDALONE
    // PC/Mac
#endif

#if UNITY_EDITOR
    // 只在編輯器（見 editor-tools.md，UnityEditor API 不能進 build）
#endif

#if DEVELOPMENT_BUILD
    // 只在 Development Build（除錯工具、作弊，見 build-command-line.md）
#endif
```

- **平台差異集中，不散落**：`#if UNITY_IOS` 散落全專案 = 每個平台都是驚喜箱——收攏到**平台抽象層**（介面 + 平台實作），業務程式碼不碰 `#if`（對應 game-dev build-automation 的平台差異集中管理）。
- **自訂符號**：Player Settings 的 Scripting Define Symbols 加自己的（`USE_STEAM`、`DEMO_BUILD`）——功能開關資料化，不硬編。

## Player Settings 與平台需求

每個平台有各自的設定與硬性要求，發版前踩雷高發區（見 game-dev build-release-checklist 的平台提交）：

- **圖示 / 啟動畫面 / Bundle ID**：每平台一套——參數化進 build 腳本。
- **權限與能力**：iOS 的 Info.plist（相機/定位用途說明，缺了審核駁回）、Android 的 permissions、min SDK。
- **方向 / 解析度 / 安全區**：手機瀏海與圓角（見 game-dev ui-tech-specs 安全區）。
- **簽章**：Android keystore、iOS 憑證/描述檔——CI 要能取得（機密管理）。
- **API 相容等級**：.NET 版本、腳本後端（IL2CPP，見 `build-il2cpp.md`）。

## 平台效能差異

- **最弱目標平台優先建與測**（game-dev build-automation）——效能與相容問題在最弱平台最先炸，別到發版週才第一次在手機上跑。
- **移動平台的特殊約束**：記憶體緊（貼圖壓縮見 `../../unity-scripting/references/asset-import-pipeline.md`）、GPU 弱（overdraw 敏感見 `perf-rendering.md`）、發熱降頻、電量——量測在真機（見 `perf-profiling.md` 目標裝置）。
- **貼圖壓縮 per 平台**：ASTC（移動）、DXT（PC）——匯入設定按平台覆寫（見 `../../unity-scripting/references/asset-import-pipeline.md`）。

## 測試矩陣

- **build 腳本吃平台參數**：`-buildTarget` + 平台設定參數化，一個腳本建全平台（見 `build-command-line.md`）。
- **CI 多平台並行**：每平台一個 build job——別只在開發者的平台驗。
- **平台專屬回歸**：每平台過一次核心流程（見 game-dev build-release-checklist）——「Android 好 iOS 崩」很常見。

## 常見坑

- **`#if` 散落全專案**：每個平台各自為政、漏改一處就一平台壞——收攏到平台抽象層。
- **只在一個平台開發到底**：發版週第一次上別的平台，一片紅——最弱平台盡早納入 CI。
- **Player Settings 手動改**：某人本機調的設定沒進版控 / build 腳本——參數化。
- **權限/plist 漏了**：iOS 審核駁回、Android 功能失效——平台需求 beta 期就對照（game-dev build-release-checklist）。
- **貼圖壓縮沒 per 平台**：移動用了 PC 格式 → 記憶體爆或不支援——匯入按平台覆寫。
- **簽章機密進版控**：keystore/憑證明碼進 git——機密管理，CI 另注入。
