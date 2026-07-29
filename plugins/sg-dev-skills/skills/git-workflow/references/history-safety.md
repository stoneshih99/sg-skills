# 重寫歷史的安全紀律

重寫歷史（reset/amend/rebase/force push）強大也危險。這篇是把危險關進紀律的鐵律——記住這幾條，重寫歷史就不會炸到別人。

## 鐵律：已 push（共享）的歷史不要改

重寫歷史會**產生新 hash 並丟棄舊 commit**（見 `branch-merge-vs-rebase.md`、`history-rewriting.md`）。判準：

- **只在本地、還沒 push** → 隨便改（rebase、amend、reset 整理到爽）。
- **已 push 到共享分支（main、develop、別人也在的分支）** → **禁止改寫**。你改了 hash，別人的本地還是舊 hash，下次他們 pull 會爆衝突、重複 commit、或覆蓋彼此。
- **已 push 但只有你一個人的 feature 分支** → 可以改，但要 force push（見下），且確定沒別人基於它工作。

**一句話**：**重寫只對「別人還沒看到的 commit」安全。**

## Force push：要用就用帶安全鎖的

改寫了已 push 的（自己的）分支後，push 會被拒（遠端歷史分岔）。這時：

```bash
# 危險：無腦覆蓋遠端，別人剛推的東西直接消失
git push --force

# 安全：只在「遠端還是我上次看到的樣子」時才覆蓋
git push --force-with-lease
```

- **一律用 `--force-with-lease`**：它會檢查遠端 ref 是不是你預期的——若別人在你 rebase 期間推了新東西，force-with-lease 會拒絕，救你一命。`--force` 直接輾過去，別人的 commit 就沒了。
- 更保險：`--force-with-lease=<branch>:<expected-sha>` 明確指定預期。

## 動手前的安全網

重寫前先建退路（配合 `recovery-reflog.md`）：

- **危險操作前記下當前 SHA**：`git rev-parse HEAD` 或開個備份分支 `git branch backup-before-rebase`——出事直接 `git reset --hard backup`。
- **reflog 是最後防線**：即使沒備份，`git reflog` 記錄 HEAD 的每次移動，rebase/reset 之前的狀態都在裡面找得回來（見 `recovery-reflog.md`）。
- **`--hard` 與未 commit 改動**：reflog 救得回已 commit 的，**救不回沒 commit 的**——動 `--hard`/`checkout` 覆蓋前，未存的改動先 `git stash`。

## 團隊約定

- **共享分支保護**：main/develop 在 GitHub 開 branch protection（禁 force push、要 PR）——用機制擋，不靠自律。
- **rebase 前喊一聲**：若真要改一個有別人的分支，先協調，改完通知對方 `git fetch && git reset --hard origin/<branch>` 對齊。

## 常見坑

- **在 main 上 rebase/force push**：災難級——全隊歷史分岔。共享分支只 merge，不改寫。
- **`git push --force` 輾掉隊友**：對方剛推的 commit 無聲消失——永遠用 `--force-with-lease`。
- **`reset --hard` 前沒 stash**：未 commit 的改動永久消失。
- **以為 reflog 什麼都救得回**：救 commit 過的，救不了從沒 commit 的東西——重要改動先 commit 或 stash。
- **改了才想到已 push**：養成「動歷史前先問：這推出去了嗎？」的反射。
