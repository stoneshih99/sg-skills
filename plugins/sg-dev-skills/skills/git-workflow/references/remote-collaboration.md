# 遠端協作：fetch / pull / push

跟遠端同步的三個動作，最常見的誤解是「pull 是什麼」。搞清楚 fetch/pull/push 的差異，遠端操作就不會意外覆蓋或漏東西。

## fetch vs pull：關鍵差異

- **`git fetch`**：把遠端的新 commit **下載到本地**（更新 `origin/main` 這種 remote-tracking 分支），**但不動你的工作分支**。安全、無副作用——只是「看看遠端有什麼」。
- **`git pull`** = `fetch` + **整合到當前分支**（merge 或 rebase）——會改你的工作分支、可能產生 merge commit 或衝突。

```bash
git fetch origin                # 只下載，不整合——先看遠端狀態
git log HEAD..origin/main       # 看遠端比我多了什麼
git pull                        # 下載 + 整合（= fetch + merge/rebase）
```

**紀律**：不確定遠端有什麼時，先 `fetch` 看，再決定怎麼整合——比直接 `pull` 撞一堆 merge commit 或衝突可控。

## pull 的整合方式：merge vs rebase

`git pull` 的整合就是 `branch-merge-vs-rebase.md` 那個選擇：

- **`git pull`（預設 merge）**：遠端有新東西時產生 merge commit——本地一堆「Merge branch 'main' of ...」噪音。
- **`git pull --rebase`**：把你本地未推的 commit rebase 到遠端最新之上——直線、乾淨。**日常同步推薦**。
- 設定預設：`git config --global pull.rebase true`（或 `pull.ff only` 只允許快進，強迫你顯式選）。

## push：送出去

- **`git push`**：把本地 commit 送到遠端。遠端有你沒有的東西時會**被拒**（non-fast-forward）——要先 `pull`（整合遠端的）再 push。
- **push 被拒 = 遠端有新 commit**：先 `git pull --rebase`（把你的疊到遠端最新之上）再 push，保持直線。

## Force push 安全（重寫歷史後）

改寫了已 push 的分支（rebase/amend）後 push 被拒，這時：

```bash
git push --force-with-lease     # 安全：遠端還是我上次看到的樣子才覆蓋
```

- **一律 `--force-with-lease` 不用 `--force`**——它會擋掉「別人在你 rebase 期間推了新東西」的情況，救你不覆蓋隊友（完整紀律見 `history-safety.md`）。

## PR / 協作流程

- **feature 分支 → push → PR → review → 合回**（GitHub Flow，見 `branch-strategy.md`）。
- **PR 前梳理歷史**：push 前 `rebase -i` 把 WIP 碎 commit 整乾淨（見 `commit-crafting.md`）——review 的人看的是整理過的歷史。
- **同步別人的改動**：協作分支上，定期 `fetch` + `rebase`/`merge` 對方的進度，別等最後大合併。
- **認證問題**（push 被拒非因歷史）：SSH key / token 認證到錯的帳號、無寫入權——這是憑證問題不是 git 操作問題（例：SSH 認到無權帳號時改用 HTTPS + credential helper）。

## 常見坑

- **以為 pull 只是下載**：pull 會改工作分支、可能衝突——只想看遠端用 `fetch`。
- **pull 撞一堆 merge commit**：預設 merge 的噪音——設 `pull.rebase true`。
- **push 被拒就 `--force`**：輾掉遠端別人的 commit——先 pull 整合，真要 force 用 `--force-with-lease`。
- **在共享分支 force push**：災難（見 `history-safety.md`）——共享分支只快進。
- **把 fetch 當 pull**：fetch 後忘了整合，以為更新了其實工作分支沒動——fetch 只更新 origin/*，要 merge/rebase 才進工作分支。
