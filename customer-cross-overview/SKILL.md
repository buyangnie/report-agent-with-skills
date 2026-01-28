---
name: customer-cross-overview
description: |
  客户例行质量报告，面向 OD 和客户。展示合同/约定层面的总体遵从性：SLA 总体达成概览、关键违约风险提示、重大事件对合同条款影响摘要、下期保障计划。支持 DOCX 和 PPTX 输出，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "客户报告"、"客户质量报告"、"SLA 达成报告"、"合同遵从报告"
  - English: "Customer report", "Customer quality report", "SLA compliance report", "Contract compliance"

  **使用场景 / Use when:**
  - 向客户汇报服务质量
  - 展示 SLA 总体达成情况
  - 提示关键违约风险
  - 准备客户例会材料
---

# 客户例行质量报告 (customer-cross-overview)

## 目标用户

OD; Customer

## 报表内容

- SLA 总体达成概览
- 关键违约风险提示
- 重大事件对合同条款影响摘要
- 下期保障计划

## 数据依赖

- **输入文件**:
  - `Incidents-exported.xlsx`
  - `Changes-exported.xlsx`
  - `Requests-exported.xlsx`
  - `Problems-exported.xlsx`
- **数据规范**: 见 [reference.md](reference.md)

## 输出格式

- DOCX (可编辑文档)
- PPTX (演示文稿)

## 语言检测

**默认**: 英文 (`--language en`)

**中文输出**: 使用 `--language zh` 当:

- 用户消息包含中文字符
- 用户明确要求 "中文报告"、"中文版"

## 执行流程

1. 检测用户语言偏好
2. 加载 `data/` 目录下的 Excel 数据
3. 计算健康评分 (100 分制)
4. 执行周期对比 (WoW + MoM)
5. 运行风险雷达规则引擎
6. 生成趋势分析
7. 生成 AI 洞察建议
8. 输出 DOCX 和 PPTX 报表

## 使用方式

```bash
# 英文报告
python scripts/generate_report.py --language en

# 中文报告
python scripts/generate_report.py --language zh
```

## 输出文件

**英文:**

- `output/Customer_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_EN.docx`
- `output/Customer_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_EN.pptx`

**中文:**

- `output/Customer_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_CN.docx`
- `output/Customer_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_CN.pptx`

## 核心功能

- **健康评分**: 100 分制 (SLA 40%, MTTR 30%, P1/P2 20%, Backlog 10%)
- **周期对比**: 自动 WoW + MoM，数据不足时降级
- **风险雷达**: 7 条自动触发规则，带优先级
- **深色主题 PPTX**: 专业演示风格
- **双语支持**: 完整中英文本地化

## 配置

创建 `.env` 文件:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```
