# 分支策略選型

分支策略是團隊/專案級決策，選錯的代價是長命分支的合併地獄或發版混亂。三種主流策略，按團隊規模與發版節奏選。

## 三種策略

| 策略 | 分支結構 | 適合 | 痛點 |
|------|---------|------|------|
| **Trunk-Based** | 一條主幹，短命分支數小時~1天就合回（或直接推主幹 + feature flag） | 高頻整合、CI 強、個人/小團隊、持續部署 | 需要 feature flag 管未完成功能；紀律要求高 |
| **GitHub Flow** | main + feature 分支 → PR → 合回 main，main 隨時可部署 | 多數 web / SaaS / 個人專案 | 無明確 release 分支，發版靠 tag |
| **Git Flow** | main + develop + feature + release + hotfix 多層 | 有明確版本發佈週期、需要維護多版本 | 重、分支多、對持續部署過度複雜 |

## 選型準則

- **個人 / 小團隊 / 持續部署** → **Trunk-Based 或 GitHub Flow**。分支越短命，合併衝突越少（長命分支是衝突的溫床）。
- **需要正式 release 週期、維護多個已發佈版本**（如要同時修 v1.2 和開發 v2）→ Git Flow 的 release/hotfix 分支才有意義。
- **遊戲專案發版**（RC 凍結、hotfix）→ 見 game-dev 的 build-release-checklist；通常 GitHub Flow + release 分支就夠，不用完整 Git Flow。
- **拿不定** → GitHub Flow 是最安全的預設：簡單、main 可部署、PR 做 review 點。

## 核心原則（勝過選哪個策略）

- **分支短命**：不管哪種策略，feature 分支活越久，rebase/merge 的衝突越痛（二進位資產尤其無法合併）。小步快合。
- **main 永遠可用**：main/trunk 隨時能建置/部署——壞了立即修或 revert（對應 game-dev build-pipeline 的鐵律）。
- **長命分支要頻繁同步**：非得長命（大重構），就頻繁 `rebase`/`merge` main 進來，別等到最後一次大合併（見 `branch-merge-vs-rebase.md`）。

## 常見坑

- **對小專案上 Git Flow**：五層分支管一個人的專案——過度工程。GitHub Flow 就好。
- **feature 分支放到爛**：兩週不合，合併日就是災難日。
- **直接在 main 上做大功能**：沒有 feature flag 又推半成品到 main，破壞「main 可用」——用分支或 flag。
- **分支命名無章**：`test`、`fix`、`new` 一堆——用 `feature/`、`fix/` 前綴 + 描述，可搜尋。
