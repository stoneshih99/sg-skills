# 切 commit：原子性與暫存區

一個 commit 該包含什麼，是決策不是機械操作。切得好，歷史可讀、可 revert、可 review；切得爛，一顆 commit 混十件事，回退時綁手綁腳。commit **訊息格式**是個人/團隊規範（留你的 CLAUDE.md），這篇講**切分**。

## 原子 commit：一個 commit 一件事

**判準：這個 commit 能不能用一句話說完「做了什麼」，且能獨立 revert 而不留半截？**

- **好**：「修正登入按鈕在 iOS 的位移」——單一意圖、可獨立回退、可獨立 review。
- **爛**：「修 bug + 順手重構 + 改個錯字 + 加功能」——回退時想退功能卻連帶退了 bug 修復。

原則：

- **一個 commit 一個邏輯變更**：功能、修復、重構分開 commit——即使是同一次工作坐下來做的。
- **不夾帶無關改動**：修 A 時看到 B 的錯字，B 另開 commit（或至少不混進 A）。對應 game-dev 的「commit 只 stage 本次改動」。
- **每個 commit 可建置**：中間狀態不該是壞的——別把「一半的重構」單獨 commit。
- **重構與行為改變分開**：純重構（不改行為）一個 commit、改行為一個 commit——review 時一眼分辨「這是搬程式還是改邏輯」。

## 暫存區是你的切分工具

工作區改了一堆混在一起，用暫存區（staging）切成多個乾淨 commit：

```bash
git add -p              # 逐 hunk 決定要不要進這個 commit（切分神器）
git add <file>          # 只加某些檔案
git status              # 看什麼進了暫存、什麼還在工作區
git commit              # 只 commit 暫存區的
# 剩下的改動留工作區，下一個 commit 再處理
```

- **`git add -p`（patch 模式）**：一個檔案裡的不同改動分開加——「這幾行是 bug 修復進 commit A、那幾行是重構進 commit B」。這是把混亂工作區切成原子 commit 的核心工具。
- **`git commit -v`**：commit 時在編輯器裡看完整 diff，確認這顆 commit 的內容對。

## 一次做完再整理

實務上寫 code 時不會邊寫邊完美切 commit——做法是：

1. 開發時先隨手 commit（WIP、碎片都行），保住進度。
2. 推之前用 `git rebase -i`（見 `history-rewriting.md`）把碎 commit 重整成乾淨的原子 commit——squash、reorder、reword。
3. **推出去的是整理過的歷史**，本地的凌亂過程不外流。

這就是「rebase 整理自己」——本地怎麼亂沒關係，push 前梳乾淨。

## 常見坑

- **一顆 commit 混多件事**：回退、review、bisect 都變難——一個 commit 一個意圖。
- **`git add .` 全加**：夾帶無關檔案、暫存了不該進的（除錯 log、密鑰）——用 `add -p` / 指定檔案，commit 前 `git status` 檢查。
- **中間 commit 是壞的**：bisect / revert 踩到不能建置的狀態——每顆可建置，或最後 rebase 整理掉。
- **巨型 commit**：「一整天的工作」一顆——沒人 review 得動，出事無法精準回退。小而頻繁。
- **把 WIP 凌亂歷史推出去**：本地隨手 commit 沒整理就 push——推前 rebase -i 梳過。
