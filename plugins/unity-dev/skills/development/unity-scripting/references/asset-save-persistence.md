# 存檔與持久化：PlayerPrefs / JSON 檔 / 序列化選型

存檔的引擎中立原則（純資料快照、原子寫入三步、版本號＋遷移鏈、autosave 時機）在 **sg-game-dev-skills** 的 system-foundation 存檔架構一節——這篇是 Unity 落地：**存哪裡、用什麼 serializer、平台坑**。

## 存哪裡：PlayerPrefs vs 檔案

| 方式 | 適合 | 痛點 |
|------|------|------|
| **PlayerPrefs** | 設定值（音量、畫質、鍵位）——少量 key-value | 各平台後端不一（Windows 是 registry）、無原子性無版本、WebGL 限 1MB。**不是存檔系統** |
| **檔案 @ `persistentDataPath`** | 遊戲進度存檔的**唯一正解** | 要自己做原子寫入與版本（原則見 game-dev；落地見下） |

- **把整包進度 JSON 塞進 PlayerPrefs 是最常見濫用**——沒有原子性（寫到一半崩潰就整包壞）、除錯看不到檔案、平台大小限制。進度一律走檔案。
- **只寫 `Application.persistentDataPath`**：`dataPath` 是安裝目錄，行動與主機平台唯讀；桌面平台寫得進去但更新/驗證檔案時會被清掉。
- **存檔路徑集中成一個常數/服務**：之後接 Steam Cloud（同步整個資料夾）或主機平台存檔 API 時只改一處。

## 序列化選型：JsonUtility vs Newtonsoft vs binary

| 方式 | 適合 | 痛點 |
|------|------|------|
| **JsonUtility** | 結構簡單的存檔——零依賴、快 | **不支援 Dictionary、多型、頂層陣列**；只序列化 public 欄位或 `[SerializeField]`，property 不吃 |
| **Newtonsoft**（`com.unity.nuget.newtonsoft-json`） | 存檔的**預設建議**——Dictionary、多型（`TypeNameHandling` 慎用）、版本容錯 | IL2CPP stripping 會吃掉只被反射用到的型別——`[Preserve]` 或 link.xml |
| **自訂 binary / MessagePack** | 存檔巨大（回放、大世界）才值得 | 不可讀難除錯；**`BinaryFormatter` 禁用**（安全漏洞、官方棄用） |

- **JSON 可讀是除錯紅利**：存檔壞了能直接打開看、能 diff 兩份存檔——量沒大到有感之前別換 binary。
- **不要序列化 UnityEngine.Object 參照**：scene 物件與資產參照存下來是垃圾——存 id（物品 id、關卡名、Addressables key），載入時重解析（對應 game-dev 的 id 參照原則）。
- **ScriptableObject 不是存檔容器**：runtime 改 SO 在 Editor 會污染資產、build 後根本不持久（見 `asset-scriptableobject.md` 的執行期污染坑）——SO 是唯讀 config，進度存檔案。

```csharp
// 原子寫入落地：暫存檔 → 讀回驗證 → File.Replace（自動保留 .bak）
public static void SaveAtomic(string path, string json)
{
    var tmp = path + ".tmp";
    File.WriteAllText(tmp, json);
    JsonConvert.DeserializeObject<SaveData>(File.ReadAllText(tmp)); // 寫壞就丟例外，不覆蓋舊檔
    if (File.Exists(path)) File.Replace(tmp, path, path + ".bak");  // 舊檔自動變備份
    else File.Move(tmp, path);
}
```

## 存檔時機的 Unity 現實

- **行動平台沒有可靠的 `OnApplicationQuit`**：iOS/Android 使用者切走 app 後隨時可能被系統殺掉、不會再回呼——存檔掛 **`OnApplicationPause(true)`**，別賭 Quit。
- **主執行緒只做快照，寫入丟背景**：Unity API 不能在背景執行緒碰——先在主執行緒把純資料快照抓好（game-dev 的 `capture()` 聚合），序列化與 I/O 再丟 `Task.Run`/thread pool（取消與生命週期見 `script-async.md`）。
- **WebGL 寫檔要同步**：`persistentDataPath` 底層是 IndexedDB，寫完不呼叫 JS 端 `FS.syncfs` 就可能沒真的落地——關頁面存檔消失的經典來源。

## 常見坑

- **進度塞 PlayerPrefs**：無原子性、平台限制——進度走檔案，PlayerPrefs 只留設定。
- **直接覆寫存檔**：斷電/崩潰在寫入中途 = 存檔全毀——上面的 SaveAtomic 三步是底線。
- **`BinaryFormatter`**：反序列化任意程式碼執行漏洞、已棄用——JSON 或 MessagePack。
- **IL2CPP 把 serializer 需要的型別 strip 掉**：Editor 正常、真機反序列化爆——`[Preserve]`/link.xml，且**存讀測試要在 IL2CPP build 上跑**（見 `../../unity-optimization/references/build-il2cpp.md`）。
- **自己拼字串存數值**：`float.ToString()`/`Parse` 吃系統地區設定（歐語系小數點是逗號）——手拼字串一律 `CultureInfo.InvariantCulture`；用 JSON serializer 則沒這問題。
- **沒有版本號**：改個欄位老玩家存檔全報廢——檔頭帶版本 + 逐版遷移（原則與 release 必測項見 game-dev 的 system-foundation 與 build-release-checklist）。
