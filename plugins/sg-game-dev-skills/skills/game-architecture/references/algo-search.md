# 專門搜尋技術

搜尋是遊戲裡最常見的演算法需求——pathfinding、AI 決策、範圍查詢都是。先決定「圖長什麼樣、邊有沒有權重、要不要最短」，再選演算法。

## 地圖 / 圖的表示

搜尋前先決定世界怎麼表示成圖（節點 + 邊）：

- **格點（Grid）**：每格一個節點，四鄰或八鄰。實作最簡單，適合方塊 / 磚塊地圖。
- **導航網格（NavMesh）**：可行走區域切成凸多邊形，節點少、路徑自然，適合連續 3D 地形。
- **路徑點（Waypoint Graph）**：手放或生成的節點連成圖，控制力強但覆蓋不完整。

> 節點數直接決定搜尋成本。Grid 直觀但節點爆多；NavMesh 節點少、通常更快。

## 二分搜（Binary Search）

在**有序**序列上每次砍半。

- **何時用**：有序陣列查值 / 找插入位置；對「答案」單調的問題做參數二分。
- **複雜度**：O(log n)。
- **遊戲情境**：依累積權重表做加權隨機抽取、時間軸取樣查最近關鍵幀、把「最小可行值」問題轉成可判定性二分。
- **陷阱**：未排序不能用；邊界（`low <= high`、mid 取法）與重複值處理極易寫錯。

```
function binary_search(sorted, target):
    low = 0; high = length(sorted) - 1
    while low <= high:
        mid = low + (high - low) / 2      # 避免溢位
        if sorted[mid] == target: return mid
        if sorted[mid] <  target: low = mid + 1
        else: high = mid - 1
    return NOT_FOUND
```

## BFS（廣度優先）

一層一層往外擴，用佇列。

- **何時用**：**無權重**圖的最短步數 / 最少格數；洪水填充（flood fill）。
- **複雜度**：O(V + E)。
- **遊戲情境**：無權格點的最短路徑、爆炸 / 感染 / 塗色的範圍擴散、計算「距離場」。
- **陷阱**：一定要在**入列時**標記 visited，否則同一節點重複入列、記憶體與時間爆掉。

```
function bfs(start, goal):
    queue = [start]; visited = {start}; parent = {}
    while queue not empty:
        node = queue.pop_front()
        if node == goal: return reconstruct(parent, goal)
        for n in neighbors(node):
            if n not in visited:
                visited.add(n); parent[n] = node
                queue.push_back(n)
    return NO_PATH
```

## DFS（深度優先）

一路走到底再回頭，用堆疊或遞迴。

- **何時用**：連通性 / 可達性、拓撲排序、迷宮生成、需要枚舉路徑時。
- **複雜度**：O(V + E)。
- **遊戲情境**：程序化迷宮生成、關卡連通性檢查、依賴排序（科技樹 / 建造順序）。
- **陷阱**：**不保證最短路徑**；遞迴太深會爆堆疊，大圖改用顯式堆疊迭代。

## Dijkstra

有權重、無負邊時的單源最短路，用優先佇列每次取最近。

- **何時用**：**有權重**邊、要真正最短、且沒有可用的方向性啟發。
- **複雜度**：O(E log V)（用二元堆）。
- **遊戲情境**：不同地形移動成本（草 / 沼澤 / 路）、到多個目標的最短、影響力地圖傳播。
- **陷阱**：不能有負權邊；沒有啟發式時會往各方向均勻擴張，比 A* 慢。

## A*（A-star）

Dijkstra 加上「到目標的估計」啟發式，優先往目標方向探索。

- **何時用**：有權重、有單一目標、且能給出**可採納**（不高估）的啟發式（如歐氏 / 曼哈頓距離）。這是遊戲 pathfinding 的預設首選。
- **複雜度**：最壞同 Dijkstra，實務上因啟發式而快很多。
- **關鍵性質**：啟發式**不高估**真實成本 → 保證最短（admissible）；此外滿足一致性則不需重開節點。

```
function a_star(start, goal):
    open = priority_queue()
    open.push(start, priority = heuristic(start, goal))
    g = {start: 0}; parent = {}
    while open not empty:
        node = open.pop_min()
        if node == goal: return reconstruct(parent, goal)
        for n in neighbors(node):
            tentative = g[node] + cost(node, n)
            if n not in g or tentative < g[n]:
                g[n] = tentative
                f = tentative + heuristic(n, goal)   # 啟發式不可高估
                parent[n] = node
                open.push(n, priority = f)
    return NO_PATH
```

- **陷阱**：啟發式高估 → 路徑不再保證最短；啟發式與實際成本單位不一致（例如對角移動成本沒算 √2）會抖動或繞路；大量單位同時尋路要考慮分攤 / 快取 / 分幀。

## JPS（Jump Point Search）

均勻格點上對 A* 的加速：沿直線 / 對角「跳過」對稱的中間格，只在有意義的轉折點入列。

- **何時用**：**均勻成本的格點**地圖、需要大量或長距離尋路。
- **複雜度**：與 A* 同級，但常數項大幅下降，open list 小很多。
- **遊戲情境**：大型 RTS / 塔防的格點尋路。
- **陷阱**：只適用均勻成本格點；非均勻地形成本或非格點地圖不適用；實作比 A* 複雜。

## 選型速查

- 有序陣列查值 → 二分搜
- 無權最短步數 / 範圍擴散 → BFS
- 連通性 / 拓撲 / 迷宮生成 → DFS
- 有權最短、無方向啟發 → Dijkstra
- 有權最短、有單一目標 → **A***
- 均勻格點、大量長距離尋路 → JPS
