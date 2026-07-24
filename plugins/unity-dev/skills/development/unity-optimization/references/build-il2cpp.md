# IL2CPP vs Mono 與 AOT 坑

「Editor 裡好好的，build 出來就崩 / 功能失效」——Unity 最有名的一類坑，根源多半是 IL2CPP 的 AOT 編譯。這篇是 IL2CPP vs Mono 選型與 AOT 限制。

## IL2CPP vs Mono

| | Mono（JIT） | IL2CPP（AOT） |
|--|------------|--------------|
| 編譯時機 | 執行期 JIT | **建置期 AOT**（IL → C++ → 原生） |
| 效能 | 較慢 | **較快**（原生碼） |
| build 時間 | 快 | **慢**（多一層 C++ 編譯） |
| 平台 | 部分平台 | iOS/主機/WebGL **強制**、多數平台可選 |
| 反射/動態程式碼 | 完整 | **受限**（見下方 AOT 坑） |

**選型**：出貨版幾乎都用 **IL2CPP**（效能 + 多平台必需，iOS/主機沒得選）；**開發迭代**可用 Mono（build 快、反射無限制）。**關鍵**：兩者行為不同——**用 Mono 開發、IL2CPP 出貨的專案，一定要在 IL2CPP build 上實測**，別假設 Mono 過了 IL2CPP 就過。

## AOT 的核心限制：沒有執行期程式碼生成

IL2CPP 在**建置期**就把所有型別與方法編譯定案——執行期無法生成新程式碼。兩個實務後果：

### 1. 反射與序列化的型別可能被剝離

- **Managed Code Stripping**：IL2CPP 會剝掉「看起來沒被呼叫」的程式碼縮小體積——但**反射/JSON 反序列化動態用到的型別**，靜態分析看不出有被用，被剝掉 → 執行期 `TypeLoadException` / 欄位消失。
- **解法**：`link.xml` 明確保留（`<type fullname="..." preserve="all"/>`）、`[Preserve]` attribute 標記不可剝離的型別/方法。JSON/反射驅動的系統（見 `../../unity-scripting/references/asset-scriptableobject.md` 的資料驅動）尤其要顧。

### 2. 泛型的 AOT 爆炸與缺實例

- IL2CPP 要在建置期知道所有泛型的具體實例化——**執行期才決定的泛型組合**（`MakeGenericType`、某些泛型 virtual）可能沒被生成 → `ExecutionEngineException`。
- 同時，泛型用太兇會**程式碼膨脹**（每個具體型別一份）——build 變大變慢。
- **解法**：避免執行期動態泛型；必要時用 AOT 泛型提示；泛型收斂。

## 其他 IL2CPP 差異

- **build 時間長**：IL2CPP 多一層 C++ 編譯——CI 快取與增量 build 重要（見 `build-command-line.md`）。
- **平台原生外掛**：IL2CPP 下 P/Invoke、原生外掛的行為與 Mono 略有差異——實測。
- **例外/堆疊資訊**：release IL2CPP 的堆疊資訊可能較少——crash 分析要靠符號檔（見 game-dev build-release-checklist 的回報）。

## 常見坑

- **只在 Mono/Editor 測**：反射/泛型的 AOT 問題只在 IL2CPP build 現形——出貨設定的 build 一定要實測（對應 game-dev build-release-checklist 的回歸測試）。
- **Stripping 剝掉反射用的型別**：功能靜默失效、`TypeLoadException`——`link.xml` / `[Preserve]` 保留。
- **執行期動態泛型**：`ExecutionEngineException`——避免，或加 AOT 提示。
- **JSON 反序列化欄位不見**：型別被剝離——保留 + 測 IL2CPP build。
- **假設 build 很快**：IL2CPP 慢——排 CI 時間、做快取。
