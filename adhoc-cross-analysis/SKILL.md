---
name: adhoc-cross-analysis
description: |
  即席分析与对比归因报表，面向 FO/BO Leader。支持按服务/系统/客户/团队/时间/优先级组合钻取，环比同比对比，输出"结论+证据样本清单"。采用预计算分析 + LLM 描述生成模式，确保分析结果可靠。支持 DOCX 和 HTML 输出，中英文双语。

  **触发条件 / Trigger conditions:**
  - 中文: "即席分析"、"临时分析"、"帮我分析"、"哪个团队最差"、"对比一下"
  - English: "Ad-hoc analysis", "Quick analysis", "Analyze for me", "Compare", "Which team"

  **使用场景 / Use when:**
  - 需要按多维度组合钻取分析
  - 需要环比/同比对比
  - 临时性的数据分析需求
  - 需要快速获得结论和证据
---

# 即席分析与对比归因 (adhoc-cross-analysis)

## 目标用户

FO/BO Leader

## 报表内容

- 按服务/系统/客户/团队/时间/优先级组合钻取
- 环比同比对比
- 输出"结论+证据样本清单"

## 设计理念

采用**预计算分析 + LLM 描述生成**模式：

1. **意图解析**：规则优先 + 简单 LLM 分类
2. **查询执行**：纯代码实现，确定性分析
3. **描述生成**：LLM 做简单的数据→自然语言转换

## 支持的分析类型

| 类型 | 触发词 | 说明 |
|-----|--------|------|
| `ranking` | 最好/最差/Top N | 排名分析 |
| `trend` | 趋势/变化 | 趋势分析 |
| `breakdown` | 分布/构成/占比 | 分布分析 |
| `comparison` | 对比/环比/同比 | 对比分析 |
| `drilldown` | 为什么/原因 | 下钻分析 |

## 支持的维度

- **Priority**: P1/P2/P3/P4
- **Category**: 事件类别
- **Team**: 处理团队
- **Resolver**: 处理人
- **Time**: 日/周/月

## 支持的指标

- **volume**: 工单量
- **sla_rate**: SLA 达成率
- **mttr**: 平均解决时间
- **violations**: 违约数

## 数据依赖

- **输入文件**: `Incidents-exported.xlsx`（或 `OpsDataPack.xlsx`）
- **数据规范**: 见 [reference.md](reference.md)

## 输出格式

- DOCX (可编辑文档)
- HTML (Web 展示)
- JSON (结构化结果)

## 使用方式

### 命令行模式

```bash
# 排名分析
python3 scripts/main.py --query "哪个团队 SLA 最差"

# 趋势分析
python3 scripts/main.py --query "最近一个月工单量趋势"

# 对比分析
python3 scripts/main.py --query "P1 和 P2 的 MTTR 对比"

# 指定语言
python3 scripts/main.py --query "Which team has worst SLA" --language en
```

### 交互模式

```bash
python3 scripts/main.py --interactive
```

## 输出文件

- `output/Adhoc_Analysis_{timestamp}_CN.html`
- `output/Adhoc_Analysis_{timestamp}_CN.docx`
- `output/Adhoc_Analysis_{timestamp}_CN.json`

## 配置

创建 `.env` 文件:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

## 架构

```
用户输入
    ↓
意图解析 (intent_parser.py)
    ↓
查询执行 (query_executor.py) ← 预处理数据 (data_loader.py)
    ↓
描述生成 (description_generator.py)
    ↓
报告输出
```
