# AudioMixer 與 AudioSource

Unity 音訊的架構落地：AudioMixer 管混音結構（bus/ducking）、AudioSource 管播放。game-dev 的 audio-mixing-loudness（bus 結構、ducking、響度）與 audio-implementation（觸發、3D 衰減、voice 上限）是引擎中立原則，這篇是 Unity 落地。

## AudioMixer：bus 結構的落地

game-dev audio-mixing-loudness 的 bus 結構在 Unity 就是 **AudioMixer + Mixer Group**：

```
Master
├── Music
├── SFX (Player / Combat / World / Ambience 子群組)
├── UI
└── Voice
```

- **玩家音量設定對應 exposed parameter**：Mixer Group 的音量 exposed 出來，程式 `mixer.SetFloat("SFXVolume", dB)` 控制——設定選單的音量滑桿就是這個（對應 game-dev audio-mixing-loudness 的 bus = 設定選單）。
- **音量是 dB 不是線性**：exposed volume 是分貝——滑桿 0-1 要轉 dB（`Mathf.Log10(v) * 20`），直接設線性值音量曲線會怪。
- **處理掛在 Group**：壓縮、EQ、殘響掛 Mixer Group 不掛單一 AudioSource（game-dev 的處理掛 bus）。

## Snapshot 與 Ducking

- **Snapshot**：一組混音狀態的快照（正常 / 戰鬥 / 暫停 / 對話）——`snapshot.TransitionTo(time)` 平滑切換。用於狀態化的混音變化（進戰鬥壓低環境）。
- **Ducking**：對話出現壓低音樂/環境——Unity 用 **Duck Volume 效果**（sidechain）或 snapshot 切換或 exposed param 程式壓。規則兩三條就好（game-dev audio-mixing-loudness 的 ducking 紀律），恢復要慢。

## AudioSource：播放

- **2D vs 3D**：`spatialBlend`（0=2D 不隨位置、1=3D 隨距離衰減）——UI/音樂/玩家自身動作用 2D，世界中的聲源用 3D（game-dev audio-implementation 的 2D/3D 分工；玩家自己的腳步做 3D 會隨鏡頭亂飄）。
- **播放方式選型**：

| 方式 | 用途 | 注意 |
|------|------|------|
| `Play()` | 播放此 AudioSource 的 clip（可控制、可停、可循環） | 一個 source 一個聲音 |
| `PlayOneShot(clip)` | 疊放一次性音效，不打斷當前 | **同一 source 可疊多個**——命中音、UI 音 |
| `PlayClipAtPoint(clip, pos)` | 在世界某點播一次（自動建臨時 source） | **每次建 + 銷毀 GameObject**——高頻用會 GC/開銷，別在熱路徑用 |

- **一次性音效池化**：大量同時的一次性音效（子彈、命中）用 **AudioSource 池**（見 `audio-import-and-performance.md`）——別每個音效各建 source 或用 PlayClipAtPoint。

## 3D 音訊設定

- **Rolloff 曲線**：距離衰減曲線（Logarithmic/Linear/Custom）——對應 game-dev audio-implementation 的衰減；min/max distance 決定「多近不再變大、多遠聽不到」。
- **Doppler**：移動聲源的都卜勒效應——快速物體（載具）有感，靜態關掉省算。
- **方向性提示是 gameplay**：敵人腳步、遠處槍聲的 3D 定位是競技/潛行的核心回饋（game-dev audio-implementation）——這類聲音定位精度優先於好聽。

## 常見坑

- **音量設線性不轉 dB**：exposed volume 是分貝——滑桿要 log 轉換。
- **PlayClipAtPoint 熱路徑**：每次建銷毀 GameObject——高頻用 AudioSource 池。
- **玩家自身動作用 3D**：腳步隨鏡頭飄——自身動作 2D。
- **處理掛單一 source**：殘響/壓縮該掛 Mixer Group——單音只管自己。
- **ducking 規則太多**：音量像坐雲霄飛車——兩三條、恢復慢（game-dev audio-mixing-loudness）。
