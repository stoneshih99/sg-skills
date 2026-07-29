# 捕捉 UI 證據

## 證據契約

先記錄來源、權利邊界、取得時間、viewport、平台與可觀察範圍。每筆結論標示為 observation、assumption 或 missing evidence；不要把後兩者混入已觀察事實。

## 來源處理

| 來源 | 優先證據 | 不可宣稱 |
|---|---|---|
| Live website | 完整頁面、實際狀態、互動路徑、可讀 DOM | 未觸發狀態的行為 |
| HTML/CSS/JS | 原始結構、tokens、事件與動畫設定 | 外部 API 或缺少資產的實際結果 |
| Video | 技術 metadata、時間點、代表影格、可見轉換 | 未顯示的 DOM、library 或精確實作 |
| Screenshot | 畫面中的 layout、type、color、asset 與狀態 | motion、hover、loading 或 responsive 行為 |

## 捕捉流程

1. 確認來源可存取，記錄 source URL 或相對檔案路徑；不要把本機絕對路徑寫入可攜交付。
2. 網站先取得一份完整頁面證據，再從同一份證據切出依畫面順序排列的 section crops。記錄 sticky、lazy loading 或無法完整捕捉的限制。
3. 影片先讀取 duration、dimensions、frame rate 與 codec。依內容、scroll、hover、transition 或 state change 的節點選代表影格，不用固定間隔影格冒充完整狀態覆蓋。
4. HTML/CSS/JS 可存取時，搜尋結構、tokens、media queries、events 與 animation declarations；用原始行為修正單純視覺推測。
5. 依 `viewport × state × interaction` 建立最小證據矩陣。只列實際取得或可重現的 default、hover、focus、active、loading、empty、error、success、responsive 與 motion 狀態。
6. 記錄每個 image、video、font、icon 與品牌素材的來源、授權狀態及替代限制。
7. 使用 [UI evidence manifest](../templates/ui-evidence-manifest.md) 交付，並明列缺少的 viewport、狀態、互動或資產。

## 工具選擇

先檢查目前 runtime 與專案已提供的能力，再選瀏覽器、媒體工具或現有測試。只有工具確實可用時才執行：

- 瀏覽器：完整頁面、viewport、互動狀態與 console 證據。
- `ffprobe`／`ffmpeg`：本機影片 metadata 與代表影格。
- 專案測試或 Storybook：穩定重現元件 state。

工具不可用時，記錄 missing evidence 並停止該項宣稱；不要用另一種證據假裝等價。

## 品質檢查

- Full-page 與 section crops 來源一致、順序完整。
- Motion frame 附時間點與觸發情境，不只是重複畫面。
- Observation 可回指具體檔案、畫面或原始行為。
- Assumption 與 missing evidence 沒有被寫成驗收事實。
- 可攜交付沒有 checkout 絕對路徑、未授權素材或憑空補出的品牌內容。
