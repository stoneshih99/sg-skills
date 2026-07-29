# 動畫系統：Animator / Mecanim

Unity 的 Animator（Mecanim）是狀態機驅動的動畫系統——但它容易長成無人看得懂的巨型狀態圖，或跟遊戲邏輯打架。這篇是 Animator 的架構決策與坑。動畫的**遊戲設計原則**（前搖後搖、狀態機銜接、root motion 抉擇）是引擎中立，見 game-dev 的 anim-game-principles；這篇是 Unity 落地。

## Animator 狀態機的紀律

Animator Controller 是狀態機（對應 game-dev 的 state-machine-diagram / anim-game-principles 的動畫狀態機跟邏輯狀態機走）：

- **動畫狀態機跟邏輯狀態機一致**：一個邏輯狀態對應一個動畫狀態——別讓 Animator 層自己長出遊戲邏輯（「在這個動畫狀態才能攻擊」的判斷應在你的邏輯層，不是埋在 Animator 條件裡）。
- **參數驅動，程式設參數**：`animator.SetFloat/SetBool/SetTrigger` 由邏輯層設，Animator 只反映狀態——不要用 Animator 當遊戲狀態的真相來源。
- **巨型狀態圖失控**：幾十個狀態連成蜘蛛網 = 沒人維護得動——用 **Sub-State Machine** 分組、**Layer** 分身體部位（見下），或改用程式驅動的 Playable API（複雜需求）。

## Layer 與 Avatar Mask：分身體部位

- **Animation Layer + Avatar Mask**：上半身開槍 + 下半身跑步——上身一層（mask 只影響上身骨骼）、下身一層（見 game-dev system-3c 的雙層狀態機、anim-game-principles 的分層）。
- **Layer 權重**：混合多層，但層一多優先權就亂——超過 2-3 層先重想需求。

## 轉移（Transition）紀律

- **轉移時間逐條調**（對應 game-dev anim-game-principles）：idle→run 可混合 0.2s；**任何→受擊要瞬切**（Has Exit Time 關、transition duration 0）——混合會吃掉打擊感。
- **Has Exit Time 的坑**：勾了 = 要等當前動畫播到某比例才轉移——「按了攻擊卻要等跑步動畫播完」的遲鈍就是它。攻擊/受擊等即時反應**關掉 Has Exit Time**、用 Trigger 條件。
- **Trigger 沒消耗掉會殘留**：`SetTrigger` 後若沒有轉移消耗它，下次意外觸發——注意 trigger 的生命週期，或用 bool。

## Root Motion vs 程式位移

- 抉擇見 game-dev anim-game-principles / system-3c：**動作遊戲多半程式位移**（手感可控），root motion 給貼地複雜位移（翻滾、攀爬）。
- Animator 的 Apply Root Motion 開關 + `OnAnimatorMove` 自訂——全專案統一策略，混用是滑步之源。

## 動畫事件（Animation Event）

- **在動畫幀上埋事件**呼叫方法（腳步聲、生效幀開判定）——對應 game-dev system-action-combat 的「動畫事件驅動」。
- **坑：邏輯藏在動畫資產裡**——判定/傷害埋在 Animation Event 上，批次檢視困難、換動畫要重埋。game-dev 的結論是**資料時間軸驅動優於動畫事件**（見 system-action-combat）——Unity 落地時，簡單的用 Animation Event，戰鬥核心的判定用資料時間軸 + 程式驅動。

## 效能

- **大量單位的 Animator 貴**：Animator 每個都有開銷——遠處/大量單位用 Animator Culling（螢幕外不更新）、或簡化動畫、或 GPU 動畫（見 `../../unity-optimization/references/perf-dots.md` 的 VAT）。
- **Optimize Game Objects**：匯入時勾，去掉不需要的骨骼 transform 階層——省更新成本（見 `../../unity-scripting/references/asset-import-pipeline.md` 匯入設定）。

## 常見坑

- **Animator 當遊戲狀態真相**：邏輯讀 Animator 當前狀態做判斷——邏輯狀態自己管，Animator 只反映。
- **Has Exit Time 造成遲鈍**：即時反應動畫等前一個播完——關掉、用 Trigger。
- **巨型狀態圖**：蜘蛛網無人維護——Sub-State Machine / Layer 分，或 Playable API。
- **判定埋在 Animation Event 難維護**：戰鬥核心用資料時間軸（game-dev system-action-combat）。
- **大量 Animator 不 cull**：螢幕外還在算——Animator Culling。
