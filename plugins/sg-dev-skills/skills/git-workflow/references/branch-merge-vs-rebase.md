# Merge vs Rebase

整合兩條分支的兩種方式，差別在**歷史長什麼樣**與**安全性**。選錯的代價：亂成一團的歷史，或改壞別人的 commit。

## 本質差異

- **merge**：把兩條線用一個 merge commit 接起來——**保留真實發生的分岔**，歷史是圖狀。
- **rebase**：把你的 commit 一個個「重放」到目標分支頂端——**改寫成一條直線**，彷彿你從最新起點開始做。

```
merge:                        rebase:
A---B---C  (main)             A---B---C  (main)
     \       \                         \
      D---E---M (feature)               D'--E' (feature)  ← D/E 被重寫成新 commit
```

**關鍵**：rebase 產生的 `D'`、`E'` 是**全新的 commit**（新 hash）——原本的 D、E 被丟棄。這就是它的威力（乾淨）與危險（改寫歷史）的來源。

## 何時選哪個

| 情境 | 選 | 為什麼 |
|------|-----|--------|
| 整合到 `main`、保留完整歷史 | merge | 真實記錄分岔與合併點 |
| 更新自己的 feature 分支到最新 main | **rebase** | 保持 feature 是「基於最新 main 的直線」，之後 PR 乾淨 |
| 分支已 push 給別人看/協作 | **merge**（禁 rebase） | rebase 改 hash 會炸掉別人的副本（見 `history-safety.md`） |
| 想要線性、易讀的專案歷史 | rebase 為主 | 沒有一堆 merge commit 噪音 |
| 想保留「這批工作是一起做的」語意 | merge（--no-ff） | merge commit 標示 feature 邊界 |

**實務常見組合**：feature 開發中用 `rebase` 更新 main（保持直線），合回 main 時用 `merge --no-ff`（標示 feature 邊界）。這是「rebase 整理自己、merge 記錄整合」。

## Pull 也是這個選擇

`git pull` = fetch + 整合，整合方式就是這題：

- `git pull`（預設 merge）：遠端有新 commit 時產生 merge commit——本地一堆「Merge branch 'main'」噪音。
- `git pull --rebase`：把你本地未推的 commit rebase 到遠端最新之上——直線、乾淨。**日常同步推薦這個**（見 `remote-collaboration.md`）。
- 設定：`git config pull.rebase true` 讓 pull 預設 rebase。

## 常見坑

- **rebase 已 push 的分支**：改寫了別人也有的 commit，對方 pull 會爆衝突或重複——鐵律「已 push 不 rebase」（見 `history-safety.md`）。
- **rebase 到一半放棄不乾淨**：卡在衝突時 `git rebase --abort` 回到起點；`--continue` 繼續；別直接亂 reset。
- **merge commit 淹沒歷史**：每次 pull 都 merge，`git log` 全是 merge 噪音——日常用 `pull --rebase`。
- **以為 rebase 會「合併」**：rebase 不整合內容，是搬 commit——內容衝突照樣要解（見 `conflict-resolution.md`）。
