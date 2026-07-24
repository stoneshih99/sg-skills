# Shader 撰寫：Graph vs 手寫、渲染管線

Unity shader 的第一個決策不是怎麼寫，是**在哪個渲染管線寫、用 Graph 還是 HLSL**——選錯的代價是整批 shader 換管線時重寫。

## 渲染管線：綁定全專案的地基決定

| 管線 | 定位 | shader 相容 |
|------|------|------------|
| **Built-in（Legacy）** | 舊預設 | 舊 surface shader / 手寫 |
| **URP**（Universal） | 多數專案的現代預設（行動到 PC 通吃） | URP shader / Shader Graph（URP target） |
| **HDRP**（High Definition） | 高階畫面（主機/高階 PC） | HDRP shader / Shader Graph（HDRP target） |

- **shader 綁管線**：URP shader 在 Built-in 不亮（粉紅色 error material）、Shader Graph 的 target 綁特定管線——**換管線 = 所有自訂 shader 重寫**。
- **管線是專案級決定，第一天定**（對應 game-dev build-platform 的地基決定）：新專案多數選 **URP**（現代、跨平台、Shader Graph 支援好）；需要頂級畫面且只上高階平台才 HDRP；Built-in 只在維護舊專案。
- **選 URP/HDRP 後 shader 用 SRP Batcher 相容寫法**（見 `../../unity-optimization/references/perf-rendering.md` 的 SRP Batcher）——不相容的 shader 打斷合批。

## Shader Graph vs 手寫 HLSL

| | Shader Graph（可視化） | 手寫 HLSL |
|--|----------------------|-----------|
| 門檻 | 低、即時預覽、美術可用 | 高、要懂 HLSL 與管線 |
| 適合 | **多數視覺效果**（表面、溶解、扭曲、大部分風格化） | Graph 做不到的、極致效能、複雜自訂光照 |
| 除錯 | 節點預覽 | 較難 |
| 綁定 | 綁管線 target | 綁管線的 include/pass |

**選型**：**預設用 Shader Graph**——90% 的效果做得到、美術可調、跨管線切換較容易。**手寫 HLSL 留給**：Graph 表達不了的（特殊光照模型、複雜計算）、效能關鍵熱點、需要精細控制 pass 的。

## 何時值得自訂 shader（vs 用內建/資產）

- **先問能不能不寫**：內建 Lit/Unlit + 參數、Asset Store 的 shader、或 VFX 用粒子系統（見 game-dev anim-vfx-design）往往就夠。
- **自訂 shader 是維護負債**：綁管線、綁 Unity 版本、variant 管理（見 `shader-material-and-variants.md`）——為一次性效果寫自訂 shader，換版本/管線就是債。
- **風格化渲染**（卡通/描邊/漸層）通常值得自訂——那是遊戲的視覺識別；一次性小效果多半不值。

## 常見坑

- **粉紅色 material**：shader 不相容當前管線——換管線要重寫 shader，或 shader 選錯 target。
- **換管線才發現全要重寫**：管線是第一天決定——中途換 URP↔HDRP 代價巨大。
- **為小效果手寫 HLSL**：維護負債——先試 Shader Graph 或內建。
- **shader 不相容 SRP Batcher**：打斷合批、DrawCall 爆（見 perf-rendering）——URP/HDRP 用相容寫法。
- **Shader Graph 沒選對 target**：URP 的 Graph 在 HDRP 專案不亮——target 對應專案管線。
