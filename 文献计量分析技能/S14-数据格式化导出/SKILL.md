---
name: S14-数据格式化导出
description: 将清洗后的文献数据按照目标格式导出，支持 WoS、CSV 和 RIS 格式，以保证可直接在 CiteSpace 等分析工具中使用。
when_to_use: S10-结果导出后，需要将最终保留数据生成可分析文件时激活。
argument-hint: "[输入文件路径] [输出格式] 例如: '最终保留数据.txt' WoS | CSV | RIS"
---

# S14 数据格式化导出

## 定位

清洗流水线**数据输出技能**。专门负责将 S10 导出的最终保留文献数据，格式化为指定分析工具可用的输出文件。

## 输入

- S10 导出的最终保留文件（原始格式保持字段完整）
- 映射表文件（包含 verdict、noise_type、reason 等字段）

## 输出

| 输出格式 | 文件示例 | 说明 |
|-----------|----------|------|
| WoS       | _Citespace.wos | 字段顺序符合 WoS 标准，头尾完整，可直接导入 CiteSpace |
| CSV       | _Python.csv    | UTF-8 with BOM，字段可选，兼容 Python / Excel 分析 |
| RIS       | _Endnote.ris   | BibTeX / RIS 标准，方便文献管理工具使用 |

## 核心原则

1. 保持字段完整性，必要字段顺序：PT, AU, TI, SO, DE, ID, PY, VL, IS, BP, EP, DI
2. 保留原始文献信息，避免丢失字段
3. 字符编码统一为 UTF-8 或 UTF-8 with BOM
4. 可选生成副本供不同分析工具使用

## 操作流程

1. 读取 S10 最终保留文件
2. 根据 schema 对字段进行映射和重排序
3. 按目标格式输出文件到指定目录
4. 输出文件名示例：
   - 最终保留数据_WoS.wos
   - 最终保留数据_CSV.csv
   - 最终保留数据_RIS.ris

## 与其他技能接口

- **前置**：S10-结果导出
- **辅助**：S06-超长文本读取（支持大文件分块）、S09-噪音模式库（可选保留附加标记字段）
- **后续使用**：CiteSpace、Excel、Python 脚本分析、EndNote 导入等