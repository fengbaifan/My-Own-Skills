---
name: S16-CiteSpace剪枝与网络分析参考
description: 汇总 CiteSpace 常用剪枝算法及参考方法，用于分析清洗完成的文献网络结构，包括 Pathfinder、MST、Pruning Sliced Networks 等。
when_to_use: 在 S13-关键词突现分析或可视化网络分析前，提供剪枝方法参考和参数设置。
argument-hint: "[清洗完成文献网络数据]"
---

# S16 CiteSpace 剪枝与网络分析参考

## 定位

为文献计量分析提供 CiteSpace 剪枝算法与网络分析方法参考，便于 S13/后续可视化技能使用。

## 内容概览

### 1. 剪枝算法

- **Pathfinder Network Scaling**
  - 根据三角形不等式移除弱边，保留最重要的连接。
  - 参数：r、q 控制剪枝强度。

- **Pruning Sliced Networks**
  - 对每个时间片或关键词网络进行局部剪枝。
  - 移除低权重边，突出核心结构。

- **Minimum Spanning Tree (MST)**
  - 保留网络中连接所有节点的最小边权集合。
  - 常用于生成可读性较高的骨架网络。

### 2. 网络指标参考

- **节点度 (Degree Centrality)**：反映节点连接数量。
- **中介中心性 (Betweenness Centrality)**：反映节点在网络中作为中介的重要性。
- **接近中心性 (Closeness Centrality)**：节点与其他节点的平均最短路径长度。
- **聚类系数 (Clustering Coefficient)**：衡量邻居间连通程度。

### 3. 可视化建议

- 利用时间片（Time Slicing）突出动态演化。
- 节点大小可按引用次数或关键词频率调整。
- 边权可按共现强度、共同引用次数调整。
- 剪枝后网络保证可读性与学术解释性。

### 4. 参考文献

- Chen C., CiteSpace II: Detecting and visualizing emerging trends in scientific literature, Journal of the American Society for Information Science and Technology, 2006.
- Chen C., PathFinder networks, MST, and pruning algorithms in CiteSpace.

## 操作流程

1. 构建文献共引用/共词网络（可使用 S14 输出的 WoS 文件）。
2. 根据研究需求选择剪枝算法：Pathfinder / MST / Pruning Sliced Networks。
3. 调整参数，生成可视化网络。
4. 输出网络节点和边权表，用于 S13 或可视化展示。