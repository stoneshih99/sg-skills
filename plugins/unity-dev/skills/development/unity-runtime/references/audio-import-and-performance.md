# 音訊匯入與效能

Unity 音訊的記憶體/CPU 取捨主要在**匯入設定**——選錯 Load Type 是「音訊吃掉幾百 MB」或「播放時 CPU 尖刺」的根源。這篇是匯入設定決策與 voice 管理。匯入自動化見 `../../unity-scripting/references/asset-import-pipeline.md`，效能量測見 `../../unity-optimization/references/perf-profiling.md`。

## Load Type：最重要的音訊決策

匯入設定的 Load Type 決定音訊怎麼進記憶體——**記憶體 vs CPU 的取捨**：

| Load Type | 行為 | 記憶體 | CPU | 適合 |
|-----------|------|--------|-----|------|
| **Decompress On Load** | 載入時解壓成 PCM 常駐 | **高**（未壓縮） | 低（播放無解壓） | 短、高頻的音效（命中、UI、腳步） |
| **Compressed In Memory** | 壓縮常駐，播放時解壓 | 低 | **高**（每次播放解壓） | 中等長度、不那麼高頻的 |
| **Streaming** | 從磁碟串流，不常駐 | **極低** | 中 + IO | **音樂、長 ambience**（一次一兩個） |

**選型鐵律**：
- **短又高頻的音效** → Decompress On Load（記憶體換掉播放 CPU；大量命中音同時播不想每個解壓）。
- **音樂/長環境音** → Streaming（不佔記憶體，一次只有一兩個在播）。
- **中間的** → Compressed In Memory。
- **別把音樂設 Decompress On Load**：一首歌解壓成 PCM 常駐是幾十 MB 的記憶體浪費——串流。

## 壓縮格式

- **Vorbis**（預設）：有損壓縮，多數音效/音樂——品質/大小可調（Quality 滑桿）。
- **PCM**：無壓縮，最短最關鍵的音效（極短 UI）——通常沒必要。
- **ADPCM**：輕量解壓，大量同時播的短音效（腳步、碰撞）——比 Vorbis 解壓便宜。
- 平台差異：壓縮格式可 per 平台覆寫（見 `../../unity-optimization/references/build-platform.md`、`../../unity-scripting/references/asset-import-pipeline.md`）。

## Force To Mono

- **3D 音效設 mono**：3D 空間化本來就重新定位，立體聲來源浪費一半記憶體——世界音效 Force To Mono。立體聲留給音樂、2D 環境。

## Voice 管理與效能

- **同時發聲數上限**（game-dev audio-implementation 的 voice 上限）：Unity 有 Max Real Voices（真的播）與 Max Virtual Voices——超過的被虛擬化（不出聲但仍追蹤）。設合理上限，別讓上百個音效同時搶。
- **搶佔（voice stealing）**：超上限時 Unity 依優先級/音量砍——設 AudioSource 的 Priority（0 最高），確保重要音效（玩家回饋、預警）不被雜訊擠掉（game-dev audio-implementation 的優先序）。
- **距離剔除**：超出最大距離的 3D 音效不該建 source（見 `audio-mixer-and-sources.md` 的 rolloff max distance）——game-dev optimization-playbook 的少做事。
- **cooldown 防疊加**：同幀大量同音效（20 隻怪同時死）疊加炸耳——同事件節流（game-dev audio-implementation 的 cooldown），或用 voice 上限兜底。
- **DSP 成本**：Mixer 的效果（殘響、壓縮）是 CPU——大量 Group + 重效果在 Profiler（`../../unity-optimization/references/perf-profiling.md`）的 Audio 看得到。

## 載入策略

- **音訊也走 Addressables**（見 `../../unity-scripting/references/asset-loading.md`）：大量語音/音樂按需載卸，別全塞進常駐——尤其語音本地化（game-dev loc / audio）量大。
- **AudioSource 池**：大量一次性音效用 AudioSource 池（同 `../../unity-optimization/references/perf-gc-and-memory.md` 物件池）——預熱到峰值，取出設 clip + Play，播完回池。

## 常見坑

- **音樂設 Decompress On Load**：幾十 MB 常駐——串流。
- **短高頻音效設 Compressed In Memory**：每次播放解壓 CPU 尖刺——Decompress On Load。
- **3D 音效沒 Force To Mono**：浪費一半記憶體——3D 一律 mono。
- **無 voice 上限**：高峰場面上百音效搶，重要的被擠掉——設上限 + Priority。
- **PlayClipAtPoint / 每音效建 source**：GC 與開銷——AudioSource 池（見 `audio-mixer-and-sources.md`）。
- **同事件無 cooldown**：群體死亡音疊加爆音——節流。
