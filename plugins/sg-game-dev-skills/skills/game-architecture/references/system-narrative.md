# 敘事系統（Narrative）

對話、任務、劇情狀態三件。敘事是**內容複雜度**的極端案例（範式選型的資料驅動主場，見 `data-paradigm-selection.md`）：三百段對話、八十個任務全是同構資料——但它又要跟所有系統掛鉤（任務聽戰鬥事件、對話改世界狀態），接縫設計是成敗處。

## 劇情狀態：一個 flag store 統治一切

**所有敘事進度用 flag 表達**，集中一個 store：

```
world_state:
    met_blacksmith: true            # 布林：見過鐵匠
    wolves_killed: 7                # 計數：殺狼數
    chapter2_stage: "found_clue"    # 階段：章節進度

條件即資料（不是程式碼）:
    condition: all[ met_blacksmith, wolves_killed >= 5, not(betrayed_guild) ]
```

- **為什麼集中**：對話開條件、任務解鎖、NPC 換台詞、門開不開——全部查同一個 store；散在各系統的進度旗標，交叉條件（「見過鐵匠且第二章之後」）就要跨系統翻找。
- **條件是 all/any/not 的資料組合**：設計師在表裡寫條件，不寫程式——但**到此為止**，條件語言長出迴圈與變數就是自製腳本語言的滑坡（`data-config-driven.md` 的邏輯洩漏警告，敘事是最常淪陷的地方）。
- **命名規約第一天立**：`章節_對象_事件`（`ch2_blacksmith_met`）——`flag_037` 三個月後沒人知道是什麼，而敘事 flag 一輩子不能改名（存檔相容，見 `system-foundation.md` 的版本遷移）。
- **存檔即 flag store 快照**：敘事進度的序列化免費獲得；網路同步時 flag 變更走事件廣播。
- flag 只增不刪：廢棄的標記為 deprecated 留著——老存檔還帶著它。

## 對話系統：資料節點圖 + 演出分離

對話是節點圖資料：

```
node types:
    line    { speaker, text_key, next }              # text_key → 本地化表
    choice  { options: [{text_key, condition, next}] } # 選項可帶顯示條件
    branch  { condition, true_next, false_next }      # 靜默分支
    action  { command, next }                         # 改世界：發指令
```

- **text 只有 key**：對話文本第一天進本地化表（`../../game-production/references/loc-text-externalization.md`——敘事是字串量的大頭，寫死中文再抽 = 考古工程）。
- **action 走指令，不執行邏輯**：對話節點發 `give_item(x)`、`set_flag(y)` 指令給遊戲系統執行（`system-ui.md` 的指令回流同構）——對話資料裡出現數值計算就是架構事故。
- **對話與演出分離**：節點圖管「說什麼、怎麼分支」；鏡頭、表情、走位是**演出軌**（另一份資料，引用對話節點）——低成本專案演出軌可以只有「頭像+立繪位置」，但分離要在，否則想升級運鏡時對話資料全重寫。
- **跳過保護**：玩家 skip 時，被跳過節點的 action **必須照跑**（只跳演出不跳邏輯）——「跳過對話後任務沒接到」是敘事系統的經典 bug，架構上解法是 action 執行與演出播放分屬兩層。

## 任務系統：狀態機 + 事件監聽

每個任務是一台狀態機（畫法見 `../../game-diagrams/references/state-machine-diagram.md`）：

```
quest: hunt_wolves（資料表一列）
    unlock_condition: ch1_done
    objectives:
        - { type: kill,    target: wolf,  count: 5 }
        - { type: collect, target: pelt,  count: 3 }
        - { type: reach,   target: camp_marker }
    on_complete: [ set_flag(wolves_cleared), give_reward(gold, 100) ]

狀態流: locked → available → active → (objectives 全達成) → turn_in → done
                                    ↘ failed（可選）
```

- **objective 監聽事件，不輪詢**：`kill` objective 訂閱擊殺事件過濾 target——每幀掃「殺夠了沒」是 perf 的輪詢病（事件通道見 `system-foundation.md`；擊殺事件同時餵成就與遙測，見 `../../game-tooling/references/telemetry-event-design.md`——同一條事件流三處消費）。
- **objective 類型是有限集合**：kill/collect/reach/talk/interact/escort 十來種吃掉 95% 需求——新任務 = 資料表加列；真正的新玩法才加 objective 類型（加程式）。
- **任務只讀寫 flag store 與事件**：任務系統不直接呼叫戰鬥/背包——它是純粹的「條件觀察者 + 指令發射器」，這讓它可以整包 headless 測試（給事件序列、驗 flag 結果）。
- 任務日誌 UI 讀投影（`system-ui.md` 的 ViewModel）：排序、追蹤標記是 UI 態，不進任務資料。

## 分支的成本控制

分支是指數怪物：每個「重大選擇」都讓後續內容翻倍——架構管不了成本，但結構可以：

- **珍珠串**：線性主幹 + 局部分支（每顆珍珠內分支、珠間收斂）——90% 的「有選擇感」用局部分支 + 台詞變化（flag 查表換行）達成，真正的全域分支留給 1-2 個。
- **收斂點宣告**：每段分支標明「在哪個 flag 狀態收斂」——沒有收斂設計的分支圖，QA 路徑數失控。
- **可達性測試**：敘事圖 + 條件跑靜態檢查——有沒有永遠到不了的節點（條件矛盾）、有沒有卡死組合（做了 A 又做 B 之後主線斷頭）。敘事死鎖在玩家存檔裡發現時，修復代價是熱修 flag（所以 flag store 要有運維後門——`../../game-tooling/references/debug-console-and-cheats.md` 的 `set_progress` 就是為這天準備的）。

## 常見陷阱

- **對話裡長出腳本語言**：條件、變數、迴圈全塞進對話資料——三個月後你在維護一個沒有除錯器的爛語言。條件到 all/any/not 為止，邏輯走指令出去。
- **flag 散裝**：每個系統自己記進度，交叉條件靠互相 import——集中 store 是第一天的決定。
- **輪詢式 objective**：任務多了以後每幀全場掃描——事件驅動。
- **skip 吃掉 action**：跳過保護沒做，速讀玩家的任務鏈斷裂。
- **文本寫死再抽**：本地化的第一天原則在敘事系統加倍適用——字串量最大的就是這裡。
- **分支無收斂設計**：內容組合爆炸，QA 測不完、玩家卡死修不了。
