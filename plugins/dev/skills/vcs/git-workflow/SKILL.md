---
name: git-workflow
description: git 工作流的實作決策與坑——單一知識入口，六域：分支與整合（merge vs rebase 何時選、分支策略）、重寫歷史（reset soft/mixed/hard、amend、rebase -i、cherry-pick 何時用）、救援（reflog 救回丟失的 commit/branch、reset 誤操作復原、stash）、切 commit（原子性、暫存區 -p）、衝突解決（讀衝突標記、rerere）、遠端協作（fetch/pull/push 差異、force-with-lease）。當要決定 merge 還是 rebase、整理歷史、救回不見的 commit、「reset 錯了怎麼辦」、「push 被拒」、force push、解衝突，或問「git 這情況怎麼處理」時使用。實作決策級，不是 git 教學。
---

# Git 工作流（Git Workflow）

> **定位**：git 的**實作決策與坑**——「這情況該用哪個指令、為什麼、有什麼後果」。不是 git 教學（`git add` 怎麼打，Claude 已知）。commit message 格式等個人規範留使用者 CLAUDE.md。

**先查域總表，再進該家族細表。**

## 域總表

| 你的問題 | 家族 | 細表 |
|----------|------|------|
| merge 還是 rebase、分支怎麼開 | 分支整合 | ↓ Branch |
| 整理/改寫歷史（reset/amend/rebase-i/cherry-pick） | 重寫歷史 | ↓ History |
| 東西不見了、reset 錯了、想救回 | 救援 | ↓ Recovery |
| 一個 commit 該包含什麼、怎麼切 | 切 commit | ↓ Commit |
| 遇到衝突怎麼解 | 衝突 | ↓ Conflict |
| push/pull/fetch、force push | 遠端協作 | ↓ Remote |

**貫穿鐵律**：**已 push（共享）的歷史不要改**——重寫只對本地未推的 commit 安全；救援永遠先想 `reflog`（git 幾乎不真的刪東西）。

## Branch（分支與整合）

| 何時 | 讀 |
|------|-----|
| 該 merge 還是 rebase、各自的歷史後果 | `references/branch-merge-vs-rebase.md` |
| 分支策略選型：trunk-based / GitHub flow / git-flow | `references/branch-strategy.md` |

## History（重寫歷史）

| 何時 | 讀 |
|------|-----|
| reset(soft/mixed/hard)、amend、rebase -i、cherry-pick 各自何時用 | `references/history-rewriting.md` |
| 重寫歷史的安全紀律：未 push 才改、force-with-lease、共享分支禁改 | `references/history-safety.md` |

## Recovery（救援）

| 何時 | 讀 |
|------|-----|
| 東西不見了：reflog 救回 commit/branch、reset 誤操作復原、stash | `references/recovery-reflog.md` |

## Commit（切 commit）

| 何時 | 讀 |
|------|-----|
| 一個 commit 該包含什麼、暫存區 -p 切分、原子性 | `references/commit-crafting.md` |

## Conflict（衝突）

| 何時 | 讀 |
|------|-----|
| 讀衝突標記、解衝突紀律、rerere 自動重用 | `references/conflict-resolution.md` |

## Remote（遠端協作）

| 何時 | 讀 |
|------|-----|
| fetch/pull/push 差異、pull 的 merge vs rebase、force push 安全 | `references/remote-collaboration.md` |
