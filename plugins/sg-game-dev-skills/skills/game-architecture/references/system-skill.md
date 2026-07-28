# 技能系統（Attribute / Skill / Buff）

技能系統的標準拆法是三層：**Attribute（屬性）**管數值、**Skill（技能）**管主動行為、**Buff（狀態效果）**管持續修飾。三層各自純粹，互動走固定介面——混在一起的技能系統，第 20 個技能開始每加一個都在踩前面的地雷。

## 三層關係

```
Skill（施放）──套用──► Buff（持續效果）──修飾──► Attribute（數值）
    │                                              │
    └────── 讀取（傷害倍率、冷卻縮減）◄─────────────┘
                        │
                        ▼
             傷害管線（見 system-action-combat.md）
```

拆三層的理由：**變化頻率不同**。屬性公式一年改三次、buff 每個版本加十個、技能每週調參——耦合在一起時，最頻繁的改動會反覆碰到最穩定的程式。

## Attribute：分層修飾器，不改基礎值

**問題**：buff 直接 `strength += 10`，移除時 `-= 10`——兩個 buff 疊加、其中一個帶百分比、中途又升級改了基礎值，還原順序一亂數值就永久污染。

**解法**：基礎值永不被修改，最終值 = 基礎值過一遍**修飾器堆疊**：

```
final = (base + Σflat) × (1 + Σpercent_add) × Π(1 + percent_mult)
#         │        │              │                    │
#      成長/裝備  +10力量     +15%、+20% 相加      獨立乘區（稀有）

struct Modifier: source_id, stage(flat|pct_add|pct_mult), value
attribute.modifiers: List<Modifier>
```

- **移除 = 拔掉自己的 modifier**（按 source_id），不做逆運算——順序永遠不會錯。
- **計算順序寫死並文件化**：flat 先、加算百分比合併、乘算獨立——「+15% 跟 +20% 是 35% 還是 38%」是平衡設計的核心決策，必須全遊戲一致且設計師知情。
- **髒標記快取**：modifier 增減時標髒，讀取時才重算（不要每幀重算全隊全屬性——見 `../../game-tooling/references/perf-optimization-playbook.md` 的 dirty flag）。
- **衍生屬性宣告依賴**：攻擊力依賴力量 → 力量髒了連鎖標髒攻擊力。依賴關係成圖，禁環（圖的檢查見 `../../game-diagrams/references/system-relation-map.md` 同思路）。

## Skill：資料定義 + 階段執行

技能是**資料**（config-driven，見 `data-config-driven.md`），執行器是通用的：

```
skill_id: fireball
    cost: { mana: 30 }
    cooldown: 6.0
    targeting: projectile          # self / melee / projectile / ground_area
    phases:
        cast:    { duration: 0.4, interruptible: true, locks: [move] }
        launch:  { spawn: fireball_projectile, snapshot: [spell_power] }
        # 命中後的效果掛在投射物資料上：
        on_hit:  { damage: {base: 50, scale: spell_power×0.8, tags:[fire]},
                   apply_buff: burning }
```

**施放流程固定為階段機**：`檢查（cost/cooldown/能力鎖）→ cast（可打斷的前搖）→ 生效（傷害/投射物/buff）→ recovery → cooldown`。

- 每階段是狀態機的一態（能力鎖的加減綁定階段進出，見 `system-action-combat.md` 的引用計數鎖）。
- **打斷規則資料化**：cast 可被移動打斷？被受擊打斷？——是技能資料的欄位，不是寫死在打斷來源裡（否則每加一種打斷來源要改所有技能）。
- **生效走快照**：發動瞬間快照相關屬性（spell_power），投射物與 DoT 用快照結算——「施放後切裝」不回溯（同 combat 篇的投射物快照原則）。要「持續受當前屬性影響」的引導技能，顯式宣告 `snapshot: none`，這是設計決策不是實作偷懶。

**執行複雜技能用時間軸**：多段位移 + 三次判定 + 結尾 buff 的招式，phases 表達力不夠時，升級成**動作軌（timeline of actions）**——時間點 × 動作（spawn/damage/move/camera）的清單，仍是資料。這就是 data-driven 的「流程編排」典型場景（見 `data-config-driven.md` 的邏輯洩漏警告：軌上放的是參數化動作，不是腳本語言）。

## Buff：tag + 效果 + 生命週期

Buff 是一份資料 + 一組掛在事件上的效果：

```
buff_id: burning
    tags: [dot, fire, debuff]
    duration: 4.0
    stacking: refresh              # 疊加策略，見下
    effects:
        on_apply:  { vfx: burn_loop }
        on_tick:   { interval: 0.5, damage: {base: 5, tags:[fire]} }
        on_remove: { }
    modifiers:                     # 掛到 Attribute 層
        - { attr: move_speed, stage: pct_add, value: -0.15 }
```

**疊加策略是第一個要寫死的決策**，逐 buff 宣告：

| 策略 | 行為 | 典型 |
|------|------|------|
| `refresh` | 重上刷新時間，不疊效果 | 多數 debuff |
| `stack(n)` | 疊層數（效果 × 層），上限 n | 中毒疊層 |
| `independent` | 各實例獨立計時 | 不同來源的護盾 |
| `strongest` | 只保留最強的一個 | 同類光環 |

- **來源要記**：同一 buff 不同施放者算不算同一個？PvP 與多人副本必踩——`(buff_id, source)` 為鍵還是 `buff_id` 為鍵，宣告在疊加策略裡。
- **驅散與免疫走 tag**：驅散 = 移除帶 `debuff` tag 的、火免 = 拒絕帶 `fire` tag 的——用 tag 集合運算，不要列舉 buff id（每加一個 buff 就要回頭改免疫表是維護地獄）。
- **on_event hooks**：進階 buff 監聽事件（受擊時、暴擊時、擊殺時觸發 X）——效果掛進傷害管線的對應階段（見 `system-action-combat.md` 的修飾器）。

**遞迴防護**：「受擊時反傷」×「反傷觸發受擊」= 無限循環。傷害管線帶**觸發深度計數**，超過上限（如 3）就截斷並 log 警告——這條保險絲要在第一個 on_event buff 上線前裝好。

## Tick 的效能

- DoT/HoT 不要每個 buff 自己開計時器——buff 系統統一心跳（如 10Hz）批次 tick 全部到期效果（批次思維見 `data-oriented-layout.md`）。
- 大量單位時，buff 容器避免每幀遍歷：到期時間丟最小堆，只處理堆頂到期的（`algo-data-structures.md` 的 heap 排程）。

## 除錯支援

- 控制台指令：`buff add/remove <id>`、`skill cast <id>`、列出目標當前 buff 與 modifier 來源（見 `../../game-tooling/references/debug-console-and-cheats.md`）。
- 屬性面板：顯示 final 值的**組成分解**（base + 哪些 modifier）——「為什麼攻擊力是 137」要一眼可答（屍檢思維，見 debug-logging）。

## 常見陷阱

- **buff 直接改基礎值**：本篇 Attribute 節的問題——修飾器堆疊是唯一正解。
- **疊加策略沒宣告**：默認行為隨實作碰巧決定，玩家發現「某 buff 可以無限疊」時已是平衡事故。
- **技能邏輯寫成程式碼**：每個技能一個 class，第 50 個技能時沒人敢動基類——技能是資料，執行器是少數幾個通用動作。
- **打斷規則散在打斷來源**：暈眩系統知道要打斷施法、擊飛系統也知道……新增「沉默」時漏了一處。規則收在技能資料，來源只發事件。
- **忘記快照宣告**：每個生效點「讀活值還是讀快照」不明確，平衡師與工程師的認知不同步——欄位強制宣告。
