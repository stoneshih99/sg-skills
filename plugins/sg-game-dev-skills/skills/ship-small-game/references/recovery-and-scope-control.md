# 恢復與範圍控制

遇到受阻、證據不足或中斷時，先依下表保留真實狀態，再執行最小可行的解阻或恢復工作；不要以推測補上 Build、測試或授權證據。

| Condition | State | Required action |
|---|---|---|
| Missing engine/SDK/account/build tool | Blocked | 記錄缺口與最小解阻步驟 |
| Asset provenance unclear | Blocked for RC | 使用合法暫代資產或取得授權 |
| Verification cannot run | Unverified | 保留命令與所需環境 |
| Test fails | Not complete | 修復或經核准縮減範圍 |
| Scope grows after Content Complete | Gate required | 回到 scope cutting 並更新四份文件 |
| Existing project lacks docs | Reconstruct | 從 repository 證據重建狀態 |
| Session resumes | Resume | 執行最早且依賴已滿足的未完成項目 |

範圍變更必須回到 `game-design` 的 scope cutting，取得所需核准後更新 game brief、delivery roadmap、acceptance matrix 與 production status。既有專案缺少文件時，從 repository 的實作、設定、命令輸出與既有驗證證據重建這四份核心交付物；已驗證成果不必重做。

恢復時先選擇 roadmap 中最早、依賴已滿足且尚未完成的項目。完成、受阻、未驗證或縮減範圍後，都回寫 roadmap、acceptance matrix 與 production status，使下一次交接可追溯。
