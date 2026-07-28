# Timeline 與 Tween：程序化動態

不是所有「會動的東西」都該用 Animator。過場、UI 動效、簡單位移各有更輕的工具——選錯的代價是殺雞用牛刀或反過來。這篇是 Timeline / Tween / 程式動畫的選型。

## 選型：四種「讓東西動」的方式

| 方式 | 適合 | 為什麼不用別的 |
|------|------|--------------|
| **Animator（Mecanim）** | 角色動畫、有狀態的持續動作（見 `anim-mecanim.md`） | 有狀態機、混合、layer |
| **Timeline** | 過場、編排式序列（鏡頭 + 角色 + 音效 + 特效同步演出） | 多軌時間線編排，設計師可視化排 |
| **Tween 庫**（DOTween 等） | UI 動效、簡單屬性過渡（位移、淡入淡出、縮放） | 一行程式、無需 Animator 資產、可鏈式 |
| **程式手動** | 需要遊戲邏輯耦合的動態（跟隨、steering、物理性移動） | 完全可控、可即時反應（見 game-dev system-3c、algo-physics steering） |

**準則**：
- **UI 動效與簡單過渡 → Tween**（見 game-dev ui-interaction-feel 的轉場）——為一個按鈕縮放開 Animator 是殺雞牛刀，一行 `transform.DOScale(...)` 搞定。
- **編排式過場 → Timeline**（多元素同步演出，見 game-dev system-narrative 的演出軌）。
- **角色動畫 → Animator**。
- **手感/邏輯耦合的移動 → 程式**（別用動畫搬角色，見 anim-game-principles 的 root motion vs 程式位移）。

## Timeline 落地

- **Timeline 是編排不是邏輯**：它排「什麼時候發生什麼」（鏡頭切、角色動、特效放）——對應 game-dev system-narrative 的動作軌、system-action-combat 的資料時間軸。
- **Signal / Marker 觸發遊戲邏輯**：Timeline 到某點發 Signal 呼叫你的方法——過場中觸發劇情 flag、給道具（走指令，見 game-dev system-ui 的指令回流、system-narrative 的 action 走指令）。
- **可跳過（skippable）**：過場要能 skip——**跳過時被跳過的邏輯（給道具、設 flag）必須照跑**（game-dev system-narrative 的跳過保護）。Timeline 純演出、邏輯用 Signal 且 skip 時補跑。
- **Timeline 綁死物件參照**：Timeline 資產引用場景物件——換場景/實例化時要重綁（用 TimelinePlayable 的 binding 或程式綁）。

## Tween 庫紀律

- **記得殺 tween**：物件銷毀時未完成的 tween 還在跑 → 改到已銷毀物件（NullReference，同 `../../unity-scripting/references/script-async.md` 的取消綁生命週期）——`DOKill()` 綁 OnDisable/OnDestroy，或用綁定生命週期的 API。
- **UI 動效可跳過**（game-dev ui-interaction-feel）：玩家再次輸入時 tween 立即完成，不要卡著等。
- **別在 tween 裡放遊戲邏輯**：tween 管視覺過渡，結算/狀態改變走邏輯層——tween 的 OnComplete 只做「視覺到位」的收尾，不做遊戲決策。

## 效能

- **大量 tween / Timeline 有成本**：UI 一堆同時 tween、複雜 Timeline 每幀求值——UI 用髒標記減少不必要動效（見 `ui-ugui-performance.md`）、Timeline 不用時停用。
- **程式動畫的每幀成本**：`Update` 裡手動 lerp 大量物件——批次或用 Job（見 `../../unity-optimization/references/perf-dots.md`）。

## 常見坑

- **什麼都用 Animator**：UI 按鈕縮放開 Animator + 資產——Tween 一行搞定。
- **Timeline 邏輯不可跳過**：skip 過場後劇情/道具沒給——Signal + skip 補跑（game-dev system-narrative）。
- **tween 不殺**：物件死了 tween 還跑——DOKill 綁生命週期。
- **tween/Timeline 裡放遊戲決策**：視覺與邏輯混——tween 管視覺，決策走邏輯層。
- **Timeline 參照沒重綁**：實例化的物件 Timeline 指向空——程式綁 binding。
