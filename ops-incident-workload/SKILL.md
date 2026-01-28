---
name: ops-incident-workload
description: |
  BO 负载与效率洞察报表，面向 FO/BO Leader。分析人员效率：积压与老化、吞吐与处理时效、队列瓶颈、专家卡点、班次/渠道差异。支持 DOCX 和 HTML 输出，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "BO 负载报告"、"人员效率分析"、"专家工作量"、"队列瓶颈分析"
  - English: "BO workload report", "Staff efficiency analysis", "Expert workload", "Queue bottleneck"

  **使用场景 / Use when:**
  - 分析 BO 人员负载与效率
  - 识别积压与老化工单
  - 发现队列瓶颈与专家卡点
  - 分析班次/渠道差异
---

# BO 负载与效率洞察 (ops-incident-workload)

## 目标用户

FO/BO Leader

## 报表内容

- 积压与老化分析
- 吞吐与处理时效
- 队列瓶颈识别
- 专家卡点分析
- 班次/渠道差异

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
4. 执行 BO 层级识别引擎
5. 执行多维度分析:
   - 专家画像
   - 单点依赖矩阵
   - 瓶颈评分
   - 负载均衡 (Gini 系数)
   - 知识孤岛检测
   - 时间模式分析
   - 风险评估
6. 生成可视化图表
7. 生成 AI 洞察建议
8. 输出 DOCX 和 HTML 报表

## 使用方式

```bash
# 英文报告
python scripts/generate_report.py --language en

# 中文报告
python scripts/generate_report.py --language zh
```

## 输出文件

**英文:**

- `output/BO_Workload_Report_YYYY-MM-DD_to_YYYY-MM-DD_EN.docx`
- `output/BO_Workload_Report_YYYY-MM-DD_to_YYYY-MM-DD_EN.html`

**中文:**

- `output/BO_Workload_Report_YYYY-MM-DD_to_YYYY-MM-DD_CN.docx`
- `output/BO_Workload_Report_YYYY-MM-DD_to_YYYY-MM-DD_CN.html`

## 配置

创建 `.env` 文件:

```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```
