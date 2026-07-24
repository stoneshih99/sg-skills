# 主題歸屬總表（TOPIC-MAP）

> **寫新內容前查這張表**：確認主題歸哪個 plugin 哪個 hub。這是 monorepo 防「跨 plugin 重複設計」的核心工具——同一主題只該有一個家。

## 十個 hub 一覽

| Plugin | Hub（分類/入口） | 家族前綴 |
|--------|-----------------|---------|
| game-dev | `planning/game-design` | gdd- / level- / feel- / playtest- |
| game-dev | `architecture/game-architecture` | algo- / data- / system- / net- |
| game-dev | `tools/game-tooling` | debug- / perf- / telemetry- |
| game-dev | `workflow/game-production` | milestone- / build- / content- / art- / audio- / anim- / loc- / ui- |
| game-dev | `diagram/game-diagrams` | （四種圖型） |
| unity-dev | `development/unity-scripting` | script- / input- / asset- / test- / editor- |
| unity-dev | `development/unity-runtime` | physics- / net- / shader- / anim- / audio- / ui- |
| unity-dev | `development/unity-optimization` | perf- / build- |
| dev | `vcs/git-workflow` | branch- / history- / recovery- / commit- / conflict- / remote- |
| dev | `shell/shell-scripting` | safety- / text- |
| dev | `craft/clean-code` | naming- / function- / smell- |
| dev | `debugging/debug-methodology` | process- / locate- / observe- |
| dev | `regex/regex-patterns` | mechanics- / safety- / design- |

## 分層原則

**同一主題的三種問法歸不同 plugin**：

- 「該怎麼設計、為什麼、何時選哪個」→ **game-dev**（引擎中立）
- 「在 Unity 具體怎麼做、哪個 API/元件、Unity 特有的坑」→ **unity-dev**
- 「跟遊戲無關的通用工程」→ **dev**

## 重疊區的歸屬裁決（最容易重複的地方）

這些主題在兩個 plugin 都「沾得上邊」——明確裁決避免各寫一份：

| 主題 | game-dev 收 | unity-dev 收 | 裁決 |
|------|------------|-------------|------|
| **效能** | `game-tooling/perf-`：引擎中立方法論（先量測再優化、預算思維、瓶頸分類） | `unity-optimization/perf-`：Unity 具體（GC/Alloc、draw call、SRP Batcher、DOTS、Profiler） | 通用方法論→game-dev；碰到 Unity API/Profiler 數字→unity |
| **多人連線** | `game-architecture/net-`：概念與選型（預測、延遲補償、rollback、權威模型） | `unity-runtime/net-`：NGO/Netcode 具體（NetworkVariable vs RPC、ownership、NetworkTransform） | 概念/選型→game-dev；NGO 具體 API→unity |
| **音訊** | `game-production/audio-`：資產標準與驗收（響度基準、格式、命名） | `unity-runtime/audio-`：Unity 實作（AudioMixer、snapshot、空間音訊） | 標準/驗收→game-dev；引擎實作→unity |
| **UI/UX** | `game-production/ui-`：UX 規範與流程（資訊層級、可用性、在地化預留） | `unity-runtime/ui-`：uGUI/UI Toolkit 具體（Canvas、rebuild、raycast） | 規範/流程→game-dev；引擎實作→unity |
| **動畫/特效** | `game-production/anim-`：資產標準與交付 | `unity-runtime/anim-`：Animator/Timeline/VFX Graph 具體 | 標準→game-dev；引擎實作→unity |
| **建置** | `game-production/build-`：發行管線概念、版本紀律 | `unity-optimization/build-`：Unity build 具體（Addressables、AssetBundle、平台設定） | 概念/流程→game-dev；Unity build 系統→unity |
| **測試** | `game-design/playtest-`：玩測（真人玩、回饋收集） | `unity-scripting/test-`：Unity Test Framework（EditMode/PlayMode、自動化） | 完全不同東西：人玩→game-dev；程式測→unity |

## 無重疊（各自獨佔）

- game-dev 獨佔：關卡設計、手感、企畫書、演算法、資料驅動架構、系統架構、遙測、除錯工具、畫圖。
- unity-dev 獨佔：C# 腳本架構、Input System、Asset 匯入管線、Editor 擴充、Shader、物理。
- dev 獨佔：git、shell、Clean Code（語言中立可讀性/重構原則）、除錯**方法論**、regex（pattern 語言與坑）——通用工程，不會撞到另兩個 plugin。

> **clean-code 的邊界**：收語言中立的可讀性/可維護性**決策**（命名表意、抽函式、code smell→重構）；**不收**具體風格慣例（PascalCase、縮排、`_` 前綴——那是團隊/語言硬規則，留使用者 CLAUDE.md 與 formatter/linter）。也別跟 game-architecture 混：那是宏觀系統設計（領域模型 vs 資料驅動），clean-code 是微觀程式碼品質。

> **debug 的邊界（唯一 overlap 詞）**：「debug」在兩處出現但分層——dev 的 `debug-methodology` 收**怎麼找 bug 的通用方法**（重現/二分定位/讀 stack trace，語言領域中立）；game-dev 的 `game-tooling/debug-` 收**做遊戲用的除錯工具**（debug draw、作弊碼、時間控制、遊戲內日誌）。方法論→dev；動手做遊戲的除錯設施→game-dev。

> **regex vs shell 的邊界（dev 內部）**：`regex/regex-patterns` 收 **pattern 語言本身與坑**（貪婪、anchor、回溯 ReDoS、flavor 可攜、何時別用 regex）；`shell/shell-scripting` 的 `text-` 收 **grep/sed/awk 工具選型與 pipeline**。「這個 regex 為什麼 match 太多/卡死」→ regex；「該用 grep 還是 awk、怎麼串管道」→ shell。grep/sed 的 BRE/ERE flavor 差異放 regex 的 safety 家族。

> **regex ReDoS vs debug 的軟邊界（已知、可接受）**：「regex 讓服務卡死」是兩段式——症狀是服務 hang（`debug-methodology` 先定位/確認是哪條 regex），修法是 ReDoS（`regex-patterns` 的 safety 家族）。sonnet probe 時這題落 debug 是合理的（先定位再 fix），不視為誤觸、不為它調 description。

## 新增時的自問

1. 這問題是「設計/為什麼」還是「Unity 具體怎麼做」？→ 決定 game-dev vs unity。
2. 跟遊戲有關嗎？無關→dev。
3. 落到哪個 hub 的哪個家族前綴？既有家族加 reference；沒有對應域才考慮新家族/新 hub。
4. 另一個 plugin 是否已有相關篇？有→用**文字提及**互指，不重寫。
