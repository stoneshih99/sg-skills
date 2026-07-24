# Physics 計算

遊戲的移動、瞄準、碰撞、平滑過渡背後都是向量數學。以下偽代碼假設 2D / 3D 向量支援基本 `+ - *(純量)`、`dot`、`length`。

## 向量基礎：點積與叉積

**點積（dot）** `a·b = ax*bx + ay*by (+ az*bz)`

- **幾何意義**：`a·b = |a||b|cosθ`。同向為正、垂直為 0、反向為負。
- **用途**：
  - 判斷敵人是否在視野前方：`dot(forward, toTarget) > 0`。
  - 求夾角：`cosθ = dot(a,b) / (|a||b|)`。
  - 投影：把速度投影到表面法線上做反彈 / 滑動。
- **陷阱**：比較夾角時，先正規化向量再取 dot，否則長度會混進結果。

**叉積（cross）**（3D 得向量，2D 得純量 `ax*by - ay*bx`）

- **用途**：
  - 2D 判斷左右轉向 / 點在線的哪一側：叉積正負。
  - 3D 求兩向量的法線（面朝向、旋轉軸）。
- **陷阱**：3D 叉積不可交換（`a×b = -(b×a)`），順序決定方向。

```
function is_in_front(forward, from, to):
    dir = normalize(to - from)
    return dot(normalize(forward), dir) > 0
```

## 插值（Interpolation）

**Lerp（線性插值）** `lerp(a, b, t) = a + (b - a) * t`，`t ∈ [0,1]`。

- **用途**：平滑移動、數值過渡、顏色漸變、攝影機跟隨。
- **陷阱**：
  - 每幀 `pos = lerp(pos, target, t)` 是**指數趨近**（framerate 相依），不是等速；要 framerate 無關需用 `t = 1 - exp(-k * dt)`。
  - 角度用一般 lerp 會在 0/360 邊界繞遠路，改用角度差取最短或 slerp。

**Slerp（球面插值）**：沿球面等角速度插值，用於旋轉 / 方向。

- **用途**：轉向、砲塔瞄準的等速轉動、attitude 過渡。
- **陷阱**：兩端幾乎反向時退化，需處理；四元數要注意取最短弧（必要時取反其中一端）。

## 碰撞偵測（Collision Detection）

由便宜到昂貴，先做寬鬆剔除再做精確判定。

**AABB（軸對齊包圍盒）重疊**——最便宜，當寬階段（broad phase）。

```
function aabb_overlap(a, b):
    return a.minX <= b.maxX and a.maxX >= b.minX
       and a.minY <= b.maxY and a.maxY >= b.minY
       # 3D 再加 Z 軸
```

**圓 / 球重疊**——用平方距離免開根號。

```
function circle_overlap(a, b):
    dx = a.x - b.x; dy = a.y - b.y
    rsum = a.r + b.r
    return dx*dx + dy*dy <= rsum*rsum      # 比較平方，避免 sqrt
```

**SAT（分離軸定理）**——凸多邊形精確判定，當窄階段（narrow phase）。

- **原理**：兩凸形不重疊 ⇔ 存在一條分離軸，兩者投影不重疊。逐一測試各邊法線為軸。
- **用途**：任意凸多邊形 / OBB 的精確碰撞與最小平移向量（MTV）。
- **陷阱**：只適用凸形（凹形需先拆分）；圓對多邊形要額外測「最近頂點」軸。

> 通用管線：**broad phase**（空間分割 + AABB 剔除，見 `algo-data-structures.md` 的 grid / spatial hash）→ **narrow phase**（圓 / SAT 精算）。

## Raycast

從起點沿方向射線，找最近命中。

- **用途**：射擊命中判定、視線 / 遮蔽（line of sight）、地面貼合、滑鼠選取。
- **格點 raycast**：用 DDA 逐格步進（voxel / tile 世界）。
- **陷阱**：起點剛好在表面上會自我命中，射線起點需略微偏移；連續高速物體要用 raycast 或掃掠避免**穿隧**（tunneling）。

```
# 射線 vs 圓：解 |origin + t*dir - center|² = r² 的最小非負 t
function ray_circle(origin, dir, center, r):
    m = origin - center
    b = dot(m, dir)
    c = dot(m, m) - r*r
    if c > 0 and b > 0: return MISS          # 射線背離且起點在外
    disc = b*b - c
    if disc < 0: return MISS
    t = -b - sqrt(disc)
    return max(t, 0)
```

## 彈道（Projectile）

**直線等速**：`pos(t) = origin + velocity * t`。

**重力拋物線**：`pos(t) = origin + v0 * t + 0.5 * g * t²`。

- **命中提前量（lead）**：對移動目標，求 `t` 使彈丸與目標同時到達同點——解關於 `t` 的二次式（彈速固定時），取最小正根。
- **陷阱**：大 `dt` 下離散步進會穿過薄牆（用掃掠 / 子步進）；提前量方程可能無正解（目標比彈丸快）需退回近似瞄準。

## Steering（轉向行為）

用「期望速度 − 當前速度 = 轉向力」組合出自然運動。

- **Seek / Flee**：朝 / 背離目標。`desired = normalize(target - pos) * maxSpeed; steer = desired - velocity`。
- **Arrive**：接近目標時依距離線性減速，避免過衝。
- **Pursue**：對移動目標加提前量後 Seek。
- **組合**：多個 steering 加權疊加（seek + 避障 + 分離），再 clamp 到最大力。
- **陷阱**：多力疊加易互相抵銷或抖動，需調權重並對合力設上限；避障要看**前方**而非當前位置。

## 選型速查

- 前方判定 / 投影 / 夾角 → 點積
- 左右側 / 求法線 → 叉積
- 平滑移動 / 過渡 → lerp（注意 framerate）
- 旋轉 / 方向過渡 → slerp
- 便宜寬階段剔除 → AABB / 圓平方距離
- 精確凸形碰撞 → SAT
- 射線命中 / 視線 → raycast（高速物體防穿隧）
- 自然移動 AI → steering
