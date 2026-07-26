# 結構型選型（Structural）：Adapter / Facade / Bridge / Decorator / Composite

結構型三兄弟（adapter/facade/bridge）長得像、意圖完全不同——分不清就會「什麼都叫 wrapper」。**用意圖選，不用形狀選。**

## 三兄弟裁決表

| Pattern | 意圖 | 時態 | 典型情境 |
|---------|------|------|---------|
| **Adapter** | 接口不合的**事後補救**——把既有東西轉成你要的形狀 | 事後 | 換第三方庫時只改 adapter 不改全身 |
| **Facade** | 給複雜子系統一張**簡化門面**——常用路徑一個入口 | 事後 | 音訊/網路子系統對外只露 5 個方法 |
| **Bridge** | 抽象與實作**兩軸獨立變化**的事前設計 | 事前 | 形狀 × 渲染後端、通知類型 × 發送通道 |

- **Adapter 的紀律**：第三方型別不准滲出 adapter 之外——滲出去了，換庫時 adapter 白做（「隔離第三方」是它存在的全部理由）。
- **Facade 不是牢籠**：門面之後仍可直取子系統（進階需求走原 API）——把 facade 做成唯一入口、什麼都往裡加，就孵出 god object。
- **Bridge 的進場檻最高**：**兩個維度都真的會擴**才值得（M 種抽象 × N 種實作，繼承要 M×N 個類，bridge 要 M+N）。只有一維變化 → 普通多型就好。「以後可能有第二軸」不算數（YAGNI）。

## Decorator vs 繼承

- **進場訊號是組合爆炸**：`BufferedStream`、`EncryptedStream`、`BufferedEncryptedStream`……每個功能組合一個子類 → 功能做成可堆疊的裝飾層，執行期自由組合。
- 順序敏感是特性也是坑：先加密再壓縮 ≠ 先壓縮再加密——堆疊順序要有規範。
- 遊戲圈最大的 decorator 化身是**屬性修飾器堆疊**（+10% 攻擊、+50 固定值的疊加規則）——那套的完整設計在 **sg-game-dev-skills** 的 system-skill，本質就是 decorator 的資料驅動版。

## Composite

- **樹形結構 + 對節點與整棵樹一致操作**：場景圖、UI 樹、組織架構——`node.Render()` 不分葉子還是容器。
- 引擎的場景樹、UI 樹**已經是 composite**——在引擎裡工作時是認出它、照它的規則走（別在上面再蓋一層自己的樹）。

## 一句帶過的兩個

- **Proxy**：與本體同介面、控制存取（延遲載入、權限、遠端）——網路 RPC stub 就是 proxy。
- **Flyweight**：大量實例共享不可變部分——遊戲的「共享資產＋實例狀態分離」就是它（tile 資產共享、per-cell 狀態另存——**sg-unity-dev-skills** tilemap 篇的紀律同源）。

## 常見坑

- **什麼都叫 wrapper**：說不出是 adapter（轉接）還是 facade（簡化）就還沒想清楚——意圖決定形狀與紀律。
- **Facade 變 god object**：門面吸走所有邏輯——facade 只轉發與編排，不擁有業務。
- **Adapter 疊 adapter**：A 轉 B 再轉 C——該直接寫 A→C，轉接鏈是理解成本。
- **為想像中的第二軸上 bridge**：多付一層間接十年沒用到——等第二軸真出現再重構。
- **decorator 堆疊順序無規範**：兩處組裝順序不同，行為微妙不一致。
