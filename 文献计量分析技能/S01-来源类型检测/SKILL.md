---
name: S01-来源类型检测
description: 自动识别文献数据集的来源平台、导出格式和编码方式。这是清洗流水线的第一步，所有后续技能依赖本技能的检测结果。
when_to_use: 当用户提供一个新的文献数据文件要求清洗，或切换到新数据集时激活。
argument-hint: "[数据文件路径]"
---

# S01 来源类型检测

## 定位

清洗流水线**入口技能**。在任何分析开始之前，必须先确定数据的来源平台和格式，因为不同平台的字段结构、编码方式、记录分隔符完全不同，直接影响后续所有技能的解析逻辑。

## 触发条件

- 用户提供新的数据文件
- 用户要求"开始清洗"但未指定数据格式
- 后续技能报告字段解析失败

## 检测流程

### 第一步：文件基本信息采集

读取目标文件的前 100 行和末尾 20 行，采集：

| 采集项 | 方法 |
|--------|------|
| 文件扩展名 | .txt / .csv / .xls / .xlsx / .bib / .ris / .ciw / .enw |
| 文件编码 | UTF-8 / UTF-8 BOM / GBK / GB2312 / ASCII / UTF-16 |
| 文件大小 | 字节数 + 人类可读格式 |
| 行数（估算） | 前100行平均行长 × 文件大小 |
| 行尾格式 | CRLF (Windows) / LF (Unix) / CR (旧Mac) |

### 第二步：来源平台指纹匹配

按优先级依次检测以下平台指纹：

#### Web of Science (WoS / Clarivate)

**指纹特征：**
- 首行为 `FN Clarivate Analytics Web of Science` 或 `FN Thomson Reuters Web of Science`
- 第二行为 `VR 1.0`
- 记录以两字母字段标签开头（`PT`, `AU`, `AF`, `TI`, `SO`...）
- 记录间以 `ER` 行分隔
- 末尾有 `EF` 标记

**导出格式变体：**
- **全记录纯文本** (.txt)：最完整，含 CR（引用）字段
- **全记录制表符** (.txt)：制表符分隔的扁平格式
- **BibTeX** (.bib)：`@article{...}` 格式
- **其他引文格式** (.ciw / .ris)：精简字段

**关键字段集（纯文本格式）：**
```
PT AU AF TI SO LA DT DE ID AB C1 C3 RP EM CR NR TC Z9 U1 U2 PU PI PA
SN EI BN J9 JI PD PY VL IS BP EP DI D2 PG WC WE SC OA PM UT ER
```

#### CNKI（中国知网）

**指纹特征：**
- 文件编码通常为 GBK 或 UTF-8 BOM
- 字段标签为中文（`标题`, `作者`, `来源`, `摘要`, `关键词`...）或英文缩写（`Title`, `Author`, `Source`...）
- CSV/Excel 导出：首行为列标题行
- 自定义导出 (.txt)：字段以 `{标题名}-` 开头
- 引文格式：GB/T 7714 / NoteExpress / EndNote / RefWorks

**导出格式变体：**
- **自定义导出** (.txt)：`{Title}`, `{Author}`, `{Source}` 等标签
- **Excel导出** (.xls/.xlsx)：列标题为中文字段名
- **CSV导出**：逗号/制表符分隔
- **NoteExpress** (.net)：`{Reference Type}:` 格式
- **EndNote** (.txt)：`%A`, `%T`, `%J` 等标签
- **RefWorks** (.txt)：`RT`, `A1`, `T1` 等标签

**关键字段集（自定义导出）：**
```
SrcDatabase（来源库）, Title, Author, Organ, Source, Keyword, Abstract,
PubTime, FirstDuty, Fund, CLC（中图分类号）, DBN, FileName, DOI, URL
```

#### Scopus (Elsevier)

**指纹特征：**
- CSV 首列为 `Authors` 或首行含 `"Authors","Title","Year","Source title"`
- RIS 格式：`TY  -` 开头
- BibTeX：`@ARTICLE{...}` 大写标签

**关键字段集（CSV格式）：**
```
Authors, Title, Year, Source title, Volume, Issue, Art. No., Page start,
Page end, DOI, Link, Abstract, Author Keywords, Index Keywords,
Document Type, Source, EID
```

#### PubMed / MEDLINE

**指纹特征：**
- MEDLINE 格式：`PMID-`, `TI  -`, `AB  -` 等四字母标签加连字符
- RIS 格式：标准 RIS 但含 PMID
- XML 格式：`<PubmedArticleSet>` 根元素

#### 其他平台

| 平台 | 指纹 |
|------|------|
| **Dimensions** | CSV，含 `Publication ID` 列和 `dimensions.ai` URL |
| **IEEE Xplore** | CSV，首列 `Document Title`，含 `IEEE` 期刊名 |
| **ProQuest** | RIS/CSV，含 `ProQuest document ID` |
| **万方 (Wanfang)** | GBK编码，含 `摘要` / `关键词` 中文字段 |
| **维普 (VIP/CQVIP)** | GBK编码，标签格式 `{U 标题}` |
| **Google Scholar** | BibTeX，元数据可能不完整 |

### 第三步：格式验证

确认检测结果后，进行结构验证：

1. **记录完整性**：抽取 3 条记录（首、中、尾），检查字段结构是否完整
2. **分隔符一致性**：记录间分隔符是否全局一致
3. **编码一致性**：是否存在乱码或混合编码
4. **多文件检测**：如果工作区内有多个数据文件，逐一检测并报告

### 第四步：混合来源检测

检查数据集是否为多来源合并：
- 同一文件中是否出现不同平台的字段格式
- 是否有重复的文献记录（标题+年份相同但字段结构不同）
- 文件名是否暗示合并（如 `merged_`, `combined_`, `all_`）

## 输出规范

检测完成后，以结构化方式报告：

```
=== 来源类型检测报告 ===

文件路径：[path]
文件大小：[size]
文件编码：[encoding]

来源平台：[platform_name]
导出格式：[format_type]
置信度：  高 / 中 / 低

记录分隔符：[separator]
关键字段：  [field_list]
估算记录数：[count]

验证结果：
  ✓ 记录结构完整
  ✓ 分隔符一致
  ✗ 发现3处编码异常（行号：xxx, xxx, xxx）

后续建议：
  → 推荐进入 S02-来源数据分析
  → [如有问题] 建议先修复编码 / 转换格式
```

## 用户问答环节

如果自动检测置信度为"低"或"中"，向用户确认：

1. **数据来源**：这批数据是从哪个平台导出的？
2. **导出方式**：使用了哪种导出选项？（全记录/精简/引文格式）
3. **是否合并**：数据文件是否由多次导出合并而成？
4. **编码选择**：导出时是否选择了特定编码？

## 与后续技能的接口

本技能检测结果将传递给：
- **S02-来源数据分析**：决定字段解析规则
- **S03-研究背景问询**：提供来源平台信息
- **S06-超长文本读取**：决定读取分块策略
- **S07-分批语义判定**：决定字段权重配置

**传递格式**：在日志或会话中明确记录 `来源平台` + `导出格式` + `字段映射表`。
