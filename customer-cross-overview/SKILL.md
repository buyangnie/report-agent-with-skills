---
name: customer-cross-overview
description: |
  综合运营质量报告（Comprehensive Quality Report），面向 2B 企业管理层和客户。
  整合 Incident / Change / Request / Problem 四大 ITIL 流程，输出 10-Sheet XLSX 工作簿，
  含原生 Excel 图表或 matplotlib 高级图表、AI 洞察，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "客户报告"、"客户质量报告"、"SLA 达成报告"、"运营质量报告"
  - English: "Customer report", "Quality report", "SLA compliance report", "Operations report"

  **使用场景 / Use when:**
  - 向客户/管理层汇报服务质量
  - 展示四大流程 KPI 与 SLA 达成情况
  - 跨流程关联分析与风险预警
  - 准备客户例会 / 管理层汇报材料
---

# 综合运营质量报告 (customer-cross-overview)

## 目标用户

2B 企业管理层; OD; Customer

## 报表内容

- 执行摘要（健康评分、四流程 KPI、风险雷达、趋势对比）
- Incident 分析 + SLA 深度分析
- Change 分析
- Service Request 分析
- Problem 分析
- 跨流程关联分析
- 人员与效率分析（含 Performance Matrix）
- 时间维度分析
- 行动计划

## 数据依赖

- **输入文件** (`data/` 目录):
  - `Incidents-exported.xlsx`（必需）
  - `Changes-exported.xlsx`（可选）
  - `Requests-exported.xlsx`（可选）
  - `Problems-exported.xlsx`（可选）
- **数据规范**: 见 [reference.md](reference.md)

## 输出格式

- **XLSX** (10-Sheet 工作簿，含图表与 AI 洞察)

### 图表引擎

| 引擎 | 说明 |
|------|------|
| `native` (默认) | 原生 Excel 图表，兼容性最佳 |
| `matplotlib` | 高级 PNG 图表嵌入，支持散点矩阵、仪表盘等高级图表类型 |

## 语言检测

**默认**: 双语 (`--language both`)

- `--language en` — 仅英文
- `--language zh` — 仅中文
- `--language both` — 同时生成中英文两份报告

## 执行流程

1. 检测用户语言偏好
2. 加载 `data/` 目录下的 Excel 数据（仅 Incidents 为必需）
3. 综合分析四大流程数据
4. 计算健康评分 (100 分制)
5. 执行周期对比 (WoW + MoM)
6. 运行风险雷达规则引擎 (R001-R010)
7. 生成 AI 洞察建议 (17 项，可通过 `--no-ai` 跳过)
8. 构建 10-Sheet XLSX 工作簿
9. 嵌入图表（native Excel 或 matplotlib PNG）

## 使用方式

```bash
# 双语报告（默认 native 图表）
python scripts/generate_report.py

# 英文报告，matplotlib 图表
python scripts/generate_report.py --language en --chart-engine matplotlib

# 中文报告，跳过 AI 洞察
python scripts/generate_report.py --language zh --no-ai

# 完整参数
python scripts/generate_report.py --language both --chart-engine native
```

## 输出文件

### 命名规则

```
Comprehensive_Quality_Report_{TIMESTAMP}_{LANG}_{ENGINE}.xlsx
```

- `{TIMESTAMP}` — 生成时间 `YYYYMMDD_HHMMSS`
- `{LANG}` — `EN` / `CN`
- `{ENGINE}` — `native_chart` / `matplotlib_chart`

### 示例

- `output/Comprehensive_Quality_Report_20260131_001455_CN_native_chart.xlsx`
- `output/Comprehensive_Quality_Report_20260131_001516_EN_matplotlib_chart.xlsx`

## Sheet 结构

| # | Tab 名称 (EN) | Tab 名称 (ZH) | 域前缀 |
|---|--------------|--------------|--------|
| 1 | Executive Summary | 执行摘要 | — |
| 2 | INC_Analysis | INC_事件分析 | INC_ |
| 3 | INC_SLA | INC_SLA分析 | INC_ |
| 4 | CHG_Analysis | CHG_变更分析 | CHG_ |
| 5 | SRQ_Analysis | SRQ_请求分析 | SRQ_ |
| 6 | PRO_Analysis | PRO_问题分析 | PRO_ |
| 7 | CRO_Cross-Process | CRO_跨流程关联 | CRO_ |
| 8 | CRO_Personnel | CRO_人员与效率 | CRO_ |
| 9 | CRO_Time Analysis | CRO_时间维度 | CRO_ |
| 10 | Action Plan | 行动计划 | — |

**域前缀命名规范**:
- `INC_` — Incident 单域
- `CHG_` — Change 单域
- `SRQ_` — Service Request 单域
- `PRO_` — Problem 单域
- `CRO_` — Cross-domain 跨域

## 核心功能

- **健康评分**: 100 分制加权评分
- **周期对比**: 自动 WoW + MoM，数据不足时降级
- **风险雷达**: 10 条自动触发规则 (R001-R010)，分 CRITICAL / WARNING / ATTENTION
- **AI 洞察**: 17 项洞察覆盖全部 Sheet，格式为「发现 → 原因 → 建议 → 预期效果」
- **双图表引擎**: native Excel 图表 + matplotlib 高级图表可切换
- **Performance Matrix**: 人员 Volume vs MTTR 散点矩阵（matplotlib 引擎）
- **双语支持**: 完整中英文本地化
- **图表比例自适应**: matplotlib 图表按目标高度等比缩放嵌入 Excel

## 配置

创建 `.env` 文件:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```
