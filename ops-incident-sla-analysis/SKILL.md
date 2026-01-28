---
name: ops-incident-sla-analysis
description: |
  SLA 违约归因分析报表，面向 FO/BO Leader。提供 SLA 总览、风险深入分析、已违约工单逐个分析；识别违约分布与趋势、主要归因（流程/资源/外部依赖/时间窗）、高风险对象清单与改进建议，用于管理闭环。支持 DOCX 和 HTML 输出，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "SLA 分析"、"违约分析"、"SLA 违约报告"、"违约归因"
  - English: "SLA analysis", "SLA violation report", "Breach analysis", "SLA compliance"

  **使用场景 / Use when:**
  - 需要了解 SLA 违约整体情况
  - 识别高风险工单，提前干预
  - 对已违约工单进行逐个深挖分析
  - 归因分析，制定改进措施
---

# SLA 违约归因分析 (ops-incident-sla-analysis)

## 目标用户

FO/BO Leader

## 报表内容

### 第一层：SLA 总览

- SLA 达成率总览（响应/解决）
- 违约数量与趋势（按周期）
- 按优先级/类别/团队的达成率分布

### 第二层：风险分析（尚未违约但有风险）

- 高风险工单清单（接近 SLA 阈值）
- 风险归因分类：
  - 流程因素（转派次数多、升级延迟）
  - 资源因素（人员不足、专家瓶颈）
  - 外部依赖（等待客户、第三方）
  - 时间窗因素（非工作时间、节假日）
- 风险预警与建议

### 第三层：违约深挖（已违约工单逐个分析）

- 违约工单清单（按严重程度排序）
- 逐单分析：
  - 基本信息（工单号、优先级、类别）
  - 时间线回溯（哪个环节超时）
  - 违约归因（根因分类）
  - 改进建议
- 违约模式汇总（共性问题提炼）

## 数据依赖

- **输入文件**: `Incidents-exported.xlsx`
- **数据规范**: 见 [reference.md](reference.md)

## 输出格式

- DOCX (可编辑文档)
- HTML (Web 展示)

## 语言检测

**默认**: 英文 (`--language en`)

**中文输出**: 使用 `--language zh` 当:

- 用户消息包含中文字符
- 用户明确要求 "中文报告"、"中文版"

## 执行流程

1. 检测用户语言偏好
2. 加载 `data/` 目录下的 Excel 数据
3. 数据清洗与校验
4. 执行三层分析:
   - SLA 总览计算
   - 风险识别与归因
   - 违约工单逐个分析
5. 生成可视化图表
6. 生成 AI 洞察建议
7. 输出 DOCX 和 HTML 报表

## 使用方式

```bash
# 英文报告
python scripts/generate_report.py --language en

# 中文报告
python scripts/generate_report.py --language zh
```

## 输出文件

**英文:**

- `output/SLA_Violation_Analysis_YYYY-MM-DD_to_YYYY-MM-DD_EN.docx`
- `output/SLA_Violation_Analysis_YYYY-MM-DD_to_YYYY-MM-DD_EN.html`

**中文:**

- `output/SLA_Violation_Analysis_YYYY-MM-DD_to_YYYY-MM-DD_CN.docx`
- `output/SLA_Violation_Analysis_YYYY-MM-DD_to_YYYY-MM-DD_CN.html`

## 核心功能

- **SLA 总览**: 达成率、违约数量、分布热力图
- **风险预警**: 识别接近阈值的高风险工单
- **四维归因**: 流程/资源/外部依赖/时间窗
- **逐单深挖**: 违约工单时间线回溯与根因分析
- **模式识别**: 提炼共性问题，支撑管理决策
- **双语支持**: 完整中英文本地化

## 配置

创建 `.env` 文件:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```
