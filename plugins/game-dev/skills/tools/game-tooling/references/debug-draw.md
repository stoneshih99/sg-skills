# Debug Draw（視覺化除錯）

遊戲的大量狀態是空間性的——碰撞、路徑、視野、速度。print 出座標沒有人腦能解析，畫在畫面上一眼就懂。Debug draw 是除錯工具箱裡投資報酬率最高的一項。

## 基本 API

一組立即模式（immediate mode）的繪製函式，當幀畫完就丟：

```
debug_draw_line(from, to, color, duration = 0)      # duration 0 = 只畫這幀
debug_draw_circle(center, radius, color)
debug_draw_box(min, max, color)
debug_draw_arrow(from, direction, color)             # 向量必備
debug_draw_text(world_pos, string, color)            # 空間中的文字標籤
debug_draw_path(points, color)                       # 折線
```

實作要點：

- **一行就能呼叫**：任何系統內部 `debug_draw_arrow(pos, velocity, GREEN)` 即可，不需要建物件、不需要清理。門檻高一分，大家就少用十分。
- **duration 參數**：瞬間事件（命中、觸發）畫 0.5-1 秒，否則一幀閃過看不到。
- **發佈版剝離**：用編譯開關或空實作，確保零成本。

## 分層開關

可視化多了會糊成一團。按系統分層，各自獨立開關：

```
debug_layers = { collision: off, ai: off, path: off, physics: off, ... }
debug_draw_line(..., layer = ai)     # 繪製時標層
```

配熱鍵或除錯選單切換（見 `debug-console-and-cheats.md`）。**預設全關**，追什麼開什麼。

## 常見可視化對象（清單）

按系統列舉，建專案時照抄：

**碰撞 / 物理**
- [ ] 碰撞形狀輪廓（用不同色區分 trigger / solid）
- [ ] 速度向量（箭頭，長度按比例）
- [ ] raycast：射線 + 命中點 + 命中法線
- [ ] 接地判定：接地射線與判定結果（角色腳下綠/紅）

**AI**
- [ ] 當前路徑（折線 + 目前目標節點高亮）
- [ ] 視野範圍（扇形）與「看到目標」狀態變色
- [ ] 當前狀態名稱（頭頂文字標籤：`Chase`、`Patrol`）
- [ ] 目標點 / 感興趣點標記

**關卡 / 系統**
- [ ] 觸發區域範圍
- [ ] 生成點與生成計時
- [ ] 攝影機邊界 / 死區（調攝影機手感時，見 game-feel 的 movement-feel）

**格點 / 尋路**
- [ ] 格線與格子可走性（半透明色塊）
- [ ] 尋路的 open/closed 集合（調 A* 時）

## 螢幕空間資訊

除了世界空間，留一塊螢幕角落的即時數值面板：

```
debug_watch("player.velocity", velocity)    # 每幀覆寫，自動排版
debug_watch("enemies.active", count)
```

比 log 適合「連續變化的值」——盯著它變化比事後讀日誌直觀。

## 常見陷阱

- **畫太多不分層**：全開的 debug draw 比沒有更糟——資訊糊死，重點淹沒。分層 + 預設關。
- **只畫當前狀態不畫事件**：碰撞「發生的那一瞬間」畫 0 duration 根本看不到；瞬間事件要留 0.5 秒以上。
- **除錯繪製影響效能到改變行為**：上千個 debug text 會拖垂幀率，時序 bug 因此消失（海森 bug）。分層開關同時是效能閥。
- **臨時畫完就刪**：追完 bug 把繪製碼刪掉，下次同系統出 bug 再寫一次。留著，掛到分層開關下。
