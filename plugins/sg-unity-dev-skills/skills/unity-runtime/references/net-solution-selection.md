# Unity 多人方案選型

Unity 有多套 netcode 方案，選錯的代價是「整個多人層重寫」——這是多人專案最難回頭的決策。同步模型的引擎中立選型（權威在哪、lockstep/rollback/狀態同步）先讀 game-dev 的 net-model-selection；這篇是「在 Unity 用哪個 netcode 套件」。

## 方案選型

| 方案 | 定位 | 適合 | 痛點 |
|------|------|------|------|
| **Netcode for GameObjects (NGO)** | Unity 官方，GameObject-based | 官方支援、中小型合作/PvP、想用 Unity 生態（Relay/Lobby） | 較新、大量實體效能不如 ECS |
| **Netcode for Entities** | Unity 官方，DOTS/ECS-based | 大量單位（RTS、大逃殺）、需要 ECS 效能（見 `../../unity-optimization/references/perf-dots.md`） | 要全 ECS、門檻高 |
| **Mirror** | 成熟第三方，開源 | 社群大、範例多、中型專案 | 非官方（但穩定） |
| **FishNet** | 現代第三方，開源 | 功能多（內建預測、lag comp）、效能好 | 生態小於 Mirror |
| **Photon**（PUN/Fusion/Quantum） | 託管服務 | 不想自架伺服器、快速上線；Fusion/Quantum 有預測/rollback | 綁 Photon 雲、成本、雲依賴 |

## 選型準則

先定同步模型（game-dev net-model-selection：權威 × 同步物），再選 Unity 套件：

- **中小型合作/PvP、要官方 + Unity 生態（Relay 打洞、Lobby）** → **NGO**（多數專案的合理起點）。
- **大量單位（千級 RTS/大逃殺）** → Netcode for Entities（ECS 效能）或 Photon Quantum（決定論）。
- **要內建預測/延遲補償又不想自己造**（FPS/動作）→ FishNet 或 Photon Fusion（預測見 game-dev net-prediction-and-latency）。
- **不想自架伺服器** → Photon 託管（Fusion/Quantum）——換雲依賴與成本。
- **P2P/lockstep 格鬥（rollback）** → Photon Quantum（決定論）或自建（見 game-dev net-model-selection 的 rollback 入場費）。

**鐵律：先做小 spike 驗方案**——netcode 方案的手感、除錯難度、與你 gameplay 的契合度，只有實測知道；選定後重寫成本極高（同 game-dev net-model-selection 的「不要先做單機之後加連線」）。

## 不變的原則（跨方案）

無論哪個套件，game-dev net 的引擎中立原則都成立：

- **伺服器權威、客戶端不可信**（見 game-dev net-protocol-and-connection 的安全基線）——競技/有經濟的遊戲，權威在 server，上行是 intent 不是結果（接 `../../unity-scripting/references/input-architecture.md` 的 intent 分層）。
- **重連是一等公民**（game-dev net-protocol）——行動網路斷線是常態。
- **開發期常開網路模擬**（延遲/丟包，game-dev net 的「好網路開發症候群」）——netcode 方案多有內建模擬。
- **同步什麼要挑**（狀態 vs 輸入，game-dev net-model-selection）——不影響勝負的下放客戶端權威。

## 常見坑

- **沒 spike 就選定**：方案的手感/除錯/契合度沒實測就全押——先小 spike。
- **「先單機之後加連線」**：多人是架構屬性不是功能，同步模型影響 gameplay 每一行（game-dev net-model-selection）——foundation 期就定。
- **選了大方案做小遊戲**：兩人合作用 Netcode for Entities（全 ECS）——NGO 就夠。
- **綁死託管雲沒評估成本**：Photon 的用量成本與雲依賴——上線規模前算。
- **忽略跨方案原則**：以為換套件就不用管權威/重連——那些是引擎中立的，套件只是實作。
