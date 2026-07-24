# 時間控制

時序類 bug（碰撞穿過、動畫接錯、輸入吃掉）發生在幾幀之內，肉眼跟不上。慢動作與逐幀是「把時間放大鏡」，也是調手感的必備工具。

## 基本架構：timescale

全遊戲的更新走同一個縮放後的時間：

```
game_dt = real_dt * timescale     # timescale: 1 正常, 0.1 慢動作, 0 暫停, 4 快轉

update_gameplay(game_dt)          # 遊戲邏輯用 game_dt
update_debug_ui(real_dt)          # 除錯 UI 用真實時間——暫停時選單還要能動
```

關鍵切分：**哪些系統吃縮放時間、哪些吃真實時間**。

- 吃 `game_dt`：物理、動畫、AI、計時器、粒子。
- 吃 `real_dt`：除錯 UI、控制台、攝影機除錯飛行、（通常）音樂。

這條界線劃錯，就會出現「暫停後選單不能按」或「慢動作時 UI 也變慢」。

## 功能清單

- [ ] **timescale 指令 / 滑桿**：`timescale 0.1` 慢動作觀察、`timescale 4` 快轉跳過等待（見 `debug-console-and-cheats.md`）。
- [ ] **暫停（timescale 0）**：世界凍結但除錯工具活著——此時配合自由攝影機四處檢查，是「活體解剖」模式。
- [ ] **逐幀步進（frame step）**：暫停狀態下按一下走一幀（跑一次 `update(fixed_dt)`）。追「那一瞬間發生什麼」的終極工具。
- [ ] **慢動作熱鍵**：按住某鍵臨時 0.2 倍速，鬆開恢復——比打指令順手，調手感時常駐。

```
# 逐幀步進
if paused and frame_step_pressed:
    run_one_update(FIXED_DT)      # 走固定一幀，再回到凍結
```

## 逐幀 + debug draw 組合

時間控制的真正威力在與其他工具疊加：

1. 慢動作重現 bug → 暫停在事發前 → 逐幀步進，同時看 debug draw 的碰撞框與速度向量（見 `debug-draw.md`）。
2. 調打擊感：逐幀數 hitstop 的幀數、檢查回饋層是否同幀觸發（見 `../../../planning/game-design/references/feel-impact-feedback.md`）。
3. 數輸入反應：按鍵到第一個視覺變化隔幾幀（見 `../../../planning/game-design/references/feel-input-responsiveness.md` 的 100ms 預算）。

## 與遊戲性時間縮放共存

如果遊戲本身有子彈時間 / hitstop 等機制，除錯 timescale 要**疊乘**而不是覆蓋：

```
effective_dt = real_dt * debug_timescale * gameplay_timescale
```

兩者各自獨立控制，除錯慢動作時遊戲的 hitstop 仍按比例呈現，才能在慢動作下調 hitstop。

## 常見陷阱

- **有系統偷用真實時間**：某個計時器直接讀系統時鐘，慢動作時它照常跑，狀態彼此脫節產生「只在慢動作出現的假 bug」。全專案統一從時間服務拿 dt。
- **timescale 0 造成除以零 / NaN**：有程式拿 dt 當除數。暫停用「跳過更新」或極小值防護。
- **物理在高 timescale 下穿隧**：快轉時 dt 變大，高速物體穿牆（見 physics 的穿隧問題）。物理用固定步長多次子步進，不要直接放大單步 dt。
- **只做慢不做步進**：0.05 倍速仍在流動，抓不住「就是那一幀」。逐幀步進不可省。
