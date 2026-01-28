---
name: ops-incident-quality
description: |
  Incident 质量洞察报表，面向 FO/BO Leader。分析事件量级/等级/趋势、MTTA/MTTR 分解、Top 服务/系统/队列，输出可执行的关注点与管理动作建议。支持 DOCX 和 HTML 输出，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "Incident 质量报告"、"事件质量分析"、"运维质量洞察"、"MTTR 分析"
  - English: "Incident quality report", "Incident analysis", "Ops quality insight", "MTTR analysis"

  **使用场景 / Use when:**
  - 需要了解 Incident 处理质量趋势
  - 分析 MTTA/MTTR 表现及分解
  - 识别 Top 问题服务/系统/队列
  - 生成管理层可执行的改进建议
---

# Incident 质量洞察 (ops-incident-quality)

## 目标用户
FO/BO Leader

## 报表内容
- 量级/等级/趋势分析
- MTTA/MTTR 分解
- Top 服务/系统/队列排名
- 可执行的关注点与管理动作建议

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
4. 执行多维度分析:
   - 量级趋势分析
   - 优先级分布
   - MTTA/MTTR 分解
   - Top 服务/系统/队列
   - SLA 达成分析
   - 人员效率分析
   - 时间模式分析
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
- `output/Incident_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_EN.docx`
- `output/Incident_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_EN.html`

**中文:**
- `output/Incident_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_CN.docx`
- `output/Incident_Quality_Report_YYYY-MM-DD_to_YYYY-MM-DD_CN.html`

## 配置

创建 `.env` 文件:
```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```
