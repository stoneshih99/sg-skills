# 重寫歷史工具箱

reset / amend / rebase -i / cherry-pick 都在動歷史，但各管不同的事。選錯的代價：丟工作、或改壞共享歷史。安全紀律見 `history-safety.md`（先讀鐵律）。

## reset：移動分支指標（三種模式）

`git reset <commit>` 把當前分支移到某個 commit——差別在**對暫存區與工作區做什麼**：

| 模式 | HEAD 移動 | 暫存區 | 工作區 | 用途 |
|------|----------|--------|--------|------|
| `--soft` | ✅ | 保留 | 保留 | **合併最近幾個 commit**（reset 到更早，改動全留在暫存區，重新 commit 一顆） |
| `--mixed`（預設） | ✅ | 重置 | 保留 | 取消 commit 且取消暫存，改動留工作區重新整理 |
| `--hard` | ✅ | 重置 | **丟棄** | **危險**：徹底丟棄改動回到某 commit（未 commit 的改動不可救） |

```bash
# 把最近 3 個 commit 合成 1 個（soft reset + 重新 commit）
git reset --soft HEAD~3
git commit -m "合併後的訊息"

# 丟棄本地所有未推改動，回到遠端狀態（--hard 慎用）
git reset --hard origin/main
```

**`--hard` 是唯一會丟工作的**——但已 commit 的東西仍可用 reflog 救回（見 `recovery-reflog.md`）；**未 commit 的改動 `--hard` 後真的沒了**。

## amend：改最後一個 commit

```bash
git commit --amend                    # 改訊息 / 補漏掉的檔案到上一個 commit
git commit --amend --no-edit          # 只補檔案，訊息不變
```

- 適合：剛 commit 就發現漏了一個檔案、或訊息打錯。
- **amend 產生新 hash**（改寫）——已 push 的別 amend（見 `history-safety.md`）。

## rebase -i：互動式整理一段歷史

`git rebase -i HEAD~5` 打開最近 5 個 commit 的編輯清單，逐個決定：

- `pick` 保留、`reword` 改訊息、`squash`/`fixup` 合併進前一個、`drop` 刪除、`edit` 停下來改、上下移動 = 重排順序。
- 用途：合併「WIP」碎 commit、改中間某個 commit 的訊息、拆分、重排——**推之前把本地歷史整理乾淨**。

```bash
git rebase -i HEAD~5
# 把一堆 fixup commit squash 進對應的功能 commit
```

## cherry-pick：搬單個 commit

```bash
git cherry-pick <commit>              # 把某 commit 套到當前分支
git cherry-pick <a>..<b>              # 一段範圍
```

- 適合：只要別的分支的**某一個** commit（hotfix 要進 release 又要回 main）、撿回誤刪分支的某個 commit。
- 產生新 hash（是複製不是移動）。

## 選型速查

| 想做 | 用 |
|------|-----|
| 改最後一個 commit 的訊息/檔案 | `amend` |
| 合併/重排/刪除最近幾個 commit | `rebase -i` |
| 取消 commit 但留改動重整理 | `reset --soft/--mixed` |
| 徹底丟棄回到某狀態 | `reset --hard`（慎） |
| 把別的分支的某顆 commit 拿過來 | `cherry-pick` |

## 常見坑

- **`reset --hard` 丟了未 commit 的改動**：這種救不回——動 `--hard` 前先 `git stash` 或確認沒未存的東西。
- **改了已 push 的歷史**：見 `history-safety.md` 鐵律——共享 commit 禁改。
- **rebase -i 卡衝突慌了**：`--abort` 回起點、解完 `--continue`（見 `conflict-resolution.md`）。
- **cherry-pick 造成重複 commit**：之後又 merge 該分支，同內容出現兩次——知道哪些已 pick。
