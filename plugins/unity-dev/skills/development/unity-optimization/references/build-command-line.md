# 命令列建置與 CI

「只有那台機器、那個人、點那個按鈕才建得出來」是專案的單點故障（見 game-dev build-automation 的引擎中立原則）。這篇是把 Unity build 變成一個指令的落地。

## BatchMode 命令列建置

Unity 可無 GUI 從命令列建置——CI 與一鍵 build 的基礎：

```bash
Unity -quit -batchmode -nographics \
  -projectPath /path/to/project \
  -executeMethod BuildScript.PerformBuild \
  -buildTarget Android \
  -logFile ./build.log
```

對應的 build 腳本（放 `Editor/`）：

```csharp
public static class BuildScript
{
    public static void PerformBuild()
    {
        var opts = new BuildPlayerOptions {
            scenes = EditorBuildSettings.scenes           // 或明確列
                     .Where(s => s.enabled).Select(s => s.path).ToArray(),
            target = BuildTarget.Android,
            locationPathName = "Builds/game.apk",
            options = BuildOptions.None                    // Development 版加 BuildOptions.Development
        };
        var report = BuildPipeline.BuildPlayer(opts);
        if (report.summary.result != BuildResult.Succeeded)
            EditorApplication.Exit(1);                     // CI 要靠 exit code 判斷成敗
    }
}
```

- **exit code 是 CI 的生命線**：build 失敗要 `Exit(1)`，否則 CI 以為成功——`BuildReport` 判 result 後顯式退出。
- **參數化**：平台、輸出路徑、版本號從命令列參數 / 環境變數讀（`Environment.GetCommandLineArgs()`）——一個腳本建全平台（見 `build-platform.md`）。

## 開發 vs 發佈設定

- **Development Build**（`BuildOptions.Development`）：帶 profiler 連線、debug 符號、Development 專屬程式碼——**量測效能一定用這個**（見 `perf-profiling.md`），但不出貨。
- **Release Build**：剝離 debug、開優化、剝除除錯工具（見 game-dev debug-console 的發佈版上鎖）——用編譯符號 / `BuildOptions` 切換，不手動改碼。
- **版本號自動生成**：從 git 資訊注入（`PlayerSettings.bundleVersion` + commit hash 顯示在遊戲內）——見 game-dev build-automation 的版本三件套，別手動改（忘改 = 回報的 bug 對不上版本）。

## CI 落地

- **觸發**：至少「合入 main 跑一次 build」——守住「main 可建置」（game-dev build-pipeline 的鐵律）。
- **Unity 授權**：CI 機器要處理 Unity License（Personal/Pro 的啟用），這是 Unity CI 的第一個坑——用 Unity 的 licensing CI 流程或授權伺服器。
- **快取**：Unity build 慢（Library 資料夾、import、IL2CPP 編譯）——快取 `Library/` 大幅加速，沒快取的 CI 慢到沒人理。
- **build 農場 / 雲**：Unity Cloud Build 或自架——多平台矩陣（`build-platform.md`）並行。

## Build 驗證

build 完不等於能玩（見 game-dev build-automation 煙霧測試）——CI 後自動：能啟動、進第一關跑幾秒不崩、版本號正確。可自動化就自動化。

## 常見坑

- **build 靠 Editor 按鈕**：設定活在某人編輯器裡，換機器失傳——一切收進 BuildScript + 版控。
- **失敗沒回傳 exit code**：CI 綠燈但 build 其實壞了——判 BuildReport + Exit。
- **CI 沒快取 Library**：每次冷 build 幾十分鐘——快取。
- **Unity License 沒處理**：CI 卡在啟用——先解授權流程。
- **版本號手動改**：忘改 → bug 對不上版本——從 git 自動注入。
