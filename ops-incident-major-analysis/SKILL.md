---
name: ops-incident-major-analysis
description: |
  重大事故复盘分析报表，面向 FO/BO Leader。分析重大事故 (P1/P2) 的影响面与时间线、根因与控制点、改进项闭环追踪；支持单次复盘与横向对比。支持 DOCX 和 HTML 输出，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "分析工单 {order_number}"、"复盘事故"、"事故分析"、"重大事件复盘"
  - English: "Analyze incident {order_number}", "Incident postmortem", "Major incident review"

  **使用场景 / Use when:**
  - 需要对特定重大事故进行复盘分析
  - 审视事故处理流程，识别瓶颈与延迟
  - 为复盘会议准备分析报告
  - 横向对比多个重大事故
---

# 重大事故复盘分析 (ops-incident-major-analysis)

## 目标用户

FO/BO Leader

## 报表内容

- 影响面与时间线 (基于轨迹)
- 根因与控制点分析
- 改进项闭环追踪
- 支持单次复盘与横向对比

## 数据依赖

- **输入文件**: `Incidents-exported.xlsx`、`IncidentTrail.json`
- **数据规范**: 见 [references/reference.md](references/reference.md)

## 输出格式

- DOCX (可编辑文档)
- HTML (Web 展示)

## 语言检测

**默认**: 英文 (`--language en`)

**中文输出**: 使用 `--language zh` 当:

- 用户消息包含中文字符
- 用户明确要求 "中文报告"、"中文版"

## 执行流程

1. 从用户请求中解析工单号
2. 加载事件数据 (JSON 格式)
3. 执行分析:
   - 时间分析: 响应时间、解决时间、各阶段时长、SLA 合规
   - 流程分析: 升级、转派、交接、参与人员
   - 问题检测: 使用规则引擎识别问题
   - AI 洞察: 使用 LLM 生成建议
4. 生成报表 (HTML + DOCX)
5. 返回报表路径

## 使用方式

```bash
cd scripts
python generate_report.py <order_number> [--language en|zh] [--no-llm]
```

**示例:**

```bash
# 英文报告 (含 LLM 分析)
python generate_report.py INC20250115001

# 中文报告
python generate_report.py INC20250115001 --language zh

# 不使用 LLM (仅规则分析)
python generate_report.py INC20250115001 --no-llm
```

## 输入数据格式

事件数据必须是 `data/` 目录下的 JSON 文件。完整 schema 见 [references/reference.md](references/reference.md)。

**必需结构:**

```json
{
  "incident": {
    "order_number": "INC20250115001",
    "title": "事件标题",
    "priority": "P1",
    "category": "Database",
    "status": "Resolved",
    "created_at": "2025-01-15T09:15:00+08:00",
    "resolved_at": "2025-01-15T12:45:00+08:00",
    "affected_systems": ["System A", "System B"],
    "sla": { "response_minutes": 15, "resolution_hours": 2 }
  },
  "timeline": [
    { "timestamp": "...", "event": "created|assigned|escalated|...", "actor": "...", "detail": "..." }
  ]
}
```

## 输出文件

报表生成在 `output/` 目录:

- `Major_Incident_Analysis_{order_number}_EN.html`
- `Major_Incident_Analysis_{order_number}_ZH.html`
- `Major_Incident_Analysis_{order_number}_EN.docx`
- `Major_Incident_Analysis_{order_number}_ZH.docx`

## 报表章节

1. **事件概览** - 基本信息、状态、受影响系统、SLA 状态
2. **时间线** - 事件逐条分解，带时长指示
3. **时间分析** - 响应时间、解决时间、各阶段时长
4. **流程分析** - 升级、转派、参与人员
5. **发现的问题** - 识别的问题及严重级别
6. **AI 洞察** - LLM 生成的评估、亮点、建议、预防措施

## 配置

创建 `.env` 文件:

```
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```
