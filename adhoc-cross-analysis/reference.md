# Data Contract - 即席分析

## 数据源

**文件**: `data/Incidents-exported.xlsx` 或 `data/OpsDataPack.xlsx`

## Sheet 1: SLA_Criteria

| 字段 | 类型 | 说明 |
|------|------|------|
| Priority | Text | P1/P2/P3/P4 |
| Response (minutes) | Number | 响应时间目标 |
| Resolution (hours) | Number | 解决时间目标 |

## Sheet 2: Data

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Order Number | Text | ✓ | 工单唯一标识 |
| Order Name | Text | ✓ | 工单标题 |
| Begin Date | DateTime | ✓ | 创建时间 |
| Resolution Date | DateTime | ✓ | 解决时间 |
| Resolver | Text | ✓ | 处理人 |
| Category | Text | ✓ | 类别 |
| Priority | Text | ✓ | 优先级 |
| Resolution Time(m) | Number | ✓ | 解决时间（分钟） |
| Response Time(m) | Number | ✓ | 响应时间（分钟） |
| Assignment Group | Text | 可选 | 分配团队 |
| Order Status | Text | 可选 | 工单状态 |

## 预处理数据结构

数据加载后会预计算以下聚合：

```json
{
  "summary": {
    "total": 8977,
    "period": "2024-04-19 ~ 2025-07-06",
    "sla_rate": 64.2,
    "avg_mttr": 12.5
  },
  "by_priority": {
    "P1": { "count": 50, "sla_rate": 80.0, "avg_mttr": 2.5, "violations": 10 },
    "P2": { "count": 200, "sla_rate": 75.0, "avg_mttr": 8.0, "violations": 50 }
  },
  "by_category": {
    "Network": { "count": 1000, "sla_rate": 70.0, "avg_mttr": 10.0, "violations": 300 }
  },
  "by_team": {
    "Team-A": { "count": 500, "sla_rate": 85.0, "avg_mttr": 8.0, "violations": 75 }
  },
  "by_resolver": {
    "john.doe": { "count": 100, "sla_rate": 90.0, "avg_mttr": 6.0, "violations": 10 }
  },
  "by_week": {
    "2024-W20": { "count": 150, "sla_rate": 72.0, "avg_mttr": 11.0, "violations": 42 }
  },
  "by_month": {
    "2024-04": { "count": 600, "sla_rate": 68.0, "avg_mttr": 13.0, "violations": 192 }
  },
  "comparisons": {
    "wow": { "volume_change": 5.2, "sla_change": -2.1 },
    "mom": { "volume_change": -3.1, "sla_change": 1.5 }
  }
}
```

## 意图解析规则

### 分析类型识别

| 类型 | 中文关键词 | 英文关键词 |
|------|-----------|-----------|
| ranking | 最好, 最差, 最多, 最少, 排名, Top | best, worst, most, least, top, bottom, rank |
| trend | 趋势, 变化, 增长, 下降 | trend, change, growth, decline |
| breakdown | 分布, 构成, 占比, 组成 | distribution, breakdown, composition |
| comparison | 对比, 比较, 环比, 同比, vs | compare, versus, vs, week-over-week, month-over-month |
| drilldown | 为什么, 原因, 归因 | why, reason, cause, attribution |

### 维度识别

| 维度 | 中文关键词 | 英文关键词 |
|------|-----------|-----------|
| priority | 优先级, P1, P2, P3, P4 | priority, P1, P2, P3, P4 |
| category | 类别, 分类, 类型 | category, type |
| team | 团队, 队伍, 组 | team, group |
| resolver | 人员, 处理人, 工程师 | resolver, engineer, person, staff |
| time | 时间, 日, 周, 月 | time, day, week, month |

### 指标识别

| 指标 | 中文关键词 | 英文关键词 |
|------|-----------|-----------|
| volume | 数量, 工单量, 量 | volume, count, number |
| sla_rate | SLA, 达成率, 合规 | SLA, compliance, rate |
| mttr | MTTR, 解决时间, 时效 | MTTR, resolution time |
| violations | 违约, 超时 | violations, breach |

## 输出格式

### JSON 结果结构

```json
{
  "query": "哪个团队 SLA 最差",
  "intent": {
    "type": "ranking",
    "dimension": "team",
    "metric": "sla_rate",
    "order": "asc",
    "limit": 5
  },
  "result": {
    "data": [
      { "name": "Team-C", "value": 55.2, "count": 300, "violations": 134 },
      { "name": "Team-B", "value": 62.1, "count": 450, "violations": 171 }
    ],
    "summary": "Team-C SLA 达成率最低，仅 55.2%"
  },
  "samples": [
    { "order_number": "INC001", "priority": "P1", "category": "Network", "mttr": 48.5 }
  ],
  "description": "分析显示，Team-C 的 SLA 达成率在所有团队中最低..."
}
```
