# 文献计量分析技能 (Bibliometric Analysis Skill)

## 项目概述
本项目提供完整的文献计量分析工作流，包括文献清洗、数据格式化、基础分析、趋势检测、关键词突现分析以及 CiteSpace 剪枝算法参考。适用于科学文献数据库（如 WoS、CNKI、Scopus 等），支持后续数据分析与可视化。

## 功能模块

- **S01-S05**: 数据来源检测、数据分析、研究背景问询、映射表构建、检索策略解析。
- **S06-S09**: 超长文本读取、人工复核学习、噪音模式库、重复记录检测。
- **S10-S11**: 结果导出与日志、批判性审查。
- **S14**: 数据格式化导出 (WoS plain text)。
- **S15**: 基础数据分析（统计验证文献数量、作者、期刊分布等）。
- **S13**: 关键词突现分析，整合 **S16-CiteSpace剪枝参考** 提供算法与网络分析方法。

## 流程概览
```
S01 → S02 → S03 → S04 → S05 → S07 → S10 → S11 → S14 → S15
                                   │
                                   └──→ S13 (整合 S16)
```
详细技能及流程请参考 `文献计量分析技能/项目流程图与技能整合.md`

## 使用方法

1. 准备原始文献数据（WoS/CNKI/Scopus 等）。
2. 执行 S01-S10 进行数据清洗和映射表构建。
3. 使用 S14 输出清洗后的 WoS 文件。
4. 可执行 S15 进行基础统计验证。
5. 使用 S13 进行关键词突现分析与网络趋势可视化。

## 部署方法

1. 克隆仓库：
```bash
git clone https://github.com/fengbaifan/My-Own-Skills.git
```
2. 安装 Python 依赖（如 Pandas, NumPy, Matplotlib）：
```bash
pip install -r requirements.txt
```
3. 按照每个技能的 SKILL.md 指南执行相应步骤。

## 输出文件

- 清洗后的保留数据 (WoS plain text)
- 统计分析 CSV 文件
- 关键词突现分析结果和网络可视化图
- 日志文件记录每轮清洗操作

## 参考文献

- Chen C., CiteSpace II: Detecting and visualizing emerging trends in scientific literature, Journal of the American Society for Information Science and Technology, 2006.
- Kleinberg J., Bursty and hierarchical structure in streams, Data Mining and Knowledge Discovery, 2002.

## 目录结构
```
文献计量分析技能/
├── SKILL.md (总入口)
├── schema/
├── S01-来源类型检测/
├── S02-来源数据分析/
├── ...
├── S13-关键词突现分析/
├── S14-数据格式化导出/
├── S15-基础数据分析/
├── S16-CiteSpace剪枝算法参考/
└── 项目流程图与技能整合.md
```

README 提供项目概览、功能模块、使用方法、部署步骤及流程图链接，方便新用户快速上手。