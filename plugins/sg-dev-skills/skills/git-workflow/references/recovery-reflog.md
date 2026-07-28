# 救援：reflog 與找回丟失

「commit 不見了」「reset 錯了」「分支刪掉了」——多數情況都救得回，因為 **git 幾乎不真的刪東西**，只是沒有 ref 指向它。reflog 是你的時光機。

## reflog：HEAD 的移動紀錄

`git reflog` 記錄 **HEAD 每一次移動**（commit、checkout、reset、rebase、merge…），即使那些 commit 已經沒有分支指向它們：

```bash
git reflog
# a1b2c3d HEAD@{0}: reset: moving to HEAD~3
# e4f5g6h HEAD@{1}: commit: 我以為弄丟的工作   ← 它還在！
# ...
git reset --hard e4f5g6h        # 回到那個狀態，工作救回
# 或不確定就先看： git show e4f5g6h
```

**核心觀念**：reset/rebase「丟掉」的 commit 沒有真的消失，只是失去 ref——reflog 保留它們的 SHA，用 SHA 就能救回（`reset --hard <sha>` 或 `git branch recovered <sha>`）。

## 常見救援場景

| 慘況 | 救法 |
|------|------|
| **reset --hard 錯了，commit 沒了** | `git reflog` 找 reset 前的 SHA → `git reset --hard <sha>` |
| **rebase 搞砸了** | `git reflog` 找 rebase 前的 SHA → `reset --hard <sha>`（或 rebase 當下用 `--abort`） |
| **刪錯分支** | `git reflog`（或分支的 reflog）找該分支最後的 SHA → `git branch <name> <sha>` |
| **amend 覆蓋了想留的原 commit** | reflog 找 amend 前的 SHA → cherry-pick 或 branch 出來 |
| **detached HEAD 做了 commit 又 checkout 走，commit 沒 ref** | reflog 找那顆 SHA → `git branch save <sha>` |

## stash：暫存未完成的改動

不是救援專用，但常搭配——把工作區暫時收起來：

```bash
git stash                       # 收起未 commit 的改動（工作區變乾淨）
git stash pop                   # 取回並套用（從堆疊移除）
git stash apply                 # 取回但保留在堆疊
git stash list                  # 看有哪些 stash
git stash -u                    # 連未追蹤檔案也收
```

- 用途：切分支前先收起手上的改動、`reset --hard` 前的保命（見 `history-safety.md`）。
- **stash 也進 reflog**：`git stash` 丟了也能從 `git fsck` / stash reflog 找回。

## 終極救援：fsck

reflog 也找不到時（極少），`git fsck --lost-found` 掃出所有「無 ref 的物件」（dangling commit）——連 reflog 過期清掉的都可能在。

## 重要限制

- **救得回「進過 git 的東西」**：commit 過、stash 過、加進暫存區過的——都有物件存在。
- **救不回「從沒進 git 的東西」**：`reset --hard`/`checkout` 覆蓋掉的**未 commit、未 stash** 改動——那些沒有物件，真的沒了。所以危險操作前先 commit/stash（見 `history-safety.md`）。
- **reflog 是本地的**：只記你自己的 HEAD 移動，clone 沒有你的 reflog；且有過期時間（預設 90 天，reachable 的 30 天）。

## 常見坑

- **慌了亂 reset**：出事第一步是 `git reflog` 看，別再亂動——每次操作都可能讓救援更難。
- **以為 reset --hard 不可逆**：commit 過的都在 reflog——但未 commit 的例外。
- **忘了 stash 的存在**：切分支前手上改動用 stash，不要硬 commit 半成品或丟掉。
- **依賴很久以前的 reflog**：過期會被 gc 清——重要的東西該 commit 到分支，不是躺 reflog。
