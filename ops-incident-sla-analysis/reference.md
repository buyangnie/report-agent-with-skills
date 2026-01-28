# Data Contract - SLA 违约归因分析

## 数据源

**文件**: `data/Incidents-exported.xlsx`

## Sheet 1: SLA_Criteria

定义各优先级的 SLA 目标。

| 字段 | 类型 | 示例 | 说明 |
|------|------|------|------|
| Priority | Text | P1, P2, P3, P4 | 优先级标识 |
| Response (minutes) | Number | 15 | 响应时间目标（分钟） |
| Resolution (hours) | Number | 4 | 解决时间目标（小时） |

## Sheet 2: Data

原始事件/工单数据。

| 字段 | 类型 | 必填 | 示例 | 说明 |
|------|------|------|------|------|
| Order Number | Text | ✓ | INC001234 | 工单唯一标识 |
| Order Name | Text | ✓ | Server down | 工单标题/摘要 |
| Begin Date | DateTime | ✓ | 2024-06-15 10:30 | 工单创建时间 |
| Resolution Date | DateTime | ✓ | 2024-06-15 14:45 | 工单解决时间 |
| Resolver | Text | ✓ | john.doe | 处理人/解决人 |
| Category | Text | ✓ | Network | 事件类别 |
| Priority | Text | ✓ | P1, P2, P3, P4 | 优先级 |
| Resolution Time(m) | Number | ✓ | 255 | 总解决时间（分钟） |
| Response Time(m) | Number | ✓ | 12 | 首次响应时间（分钟） |
| Suspend Time(m) | Number | 可选 | 60 | 挂起/暂停时长（分钟） |
| Order Status | Text | ✓ | Resolved | 工单状态 |
| Current Phase | Text | 可选 | Closed | 当前阶段 |
| Assignment Group | Text | 可选 | L2-Network | 分配队列/团队 |
| Escalation Count | Number | 可选 | 2 | 升级次数 |
| Reassignment Count | Number | 可选 | 3 | 转派次数 |

## 计算字段

分析引擎自动添加以下计算列：

| 字段 | 公式 | 说明 |
|------|------|------|
| Resolution_Hours | Resolution Time(m) / 60 | 解决时间（小时） |
| SLA_Response_Met | Response Time(m) <= SLA_Criteria.Response | 响应 SLA 是否达成 |
| SLA_Resolution_Met | Resolution_Hours <= SLA_Criteria.Resolution | 解决 SLA 是否达成 |
| SLA_Response_Pct | Response Time(m) / SLA_Criteria.Response * 100 | 响应时间占 SLA 百分比 |
| SLA_Resolution_Pct | Resolution_Hours / SLA_Criteria.Resolution * 100 | 解决时间占 SLA 百分比 |
| Risk_Level | 基于 SLA 百分比 | High (>80%) / Medium (60-80%) / Low (<60%) |
| Violation_Type | 基于 SLA 达成 | Response / Resolution / Both / None |

## 归因分类规则

### 流程因素

- Reassignment Count >= 3 → 转派过多
- Escalation Count >= 2 → 升级延迟
- 首次分配时间 > 30min → 初始分配慢

### 资源因素

- 同一 Resolver 同时处理 > 5 单 → 人员过载
- 特定 Category 集中于少数人 → 专家瓶颈

### 外部依赖

- Suspend Time(m) > Resolution Time(m) * 0.5 → 等待时间过长
- Order Status 包含 "Pending Customer" → 等待客户

### 时间窗因素

- Begin Date 在非工作时间 (18:00-09:00) → 非工作时间
- Begin Date 在周末/节假日 → 节假日影响

## 数据清洗规则

1. **空 Resolver** → 标记为 "Unassigned"
2. **负数解决时间** → 排除出 MTTR 计算
3. **无效日期格式** → 报错并中止
4. **缺失 Priority** → 默认为 "P4"
5. **文本字段空格** → 自动 trim

## 输出文件

生成在 `output/` 目录：

| 文件 | 格式 | 说明 |
|------|------|------|
| SLA_Violation_Analysis_*.html | HTML | Web 展示 |
| SLA_Violation_Analysis_*.docx | DOCX | 可编辑文档 |
| images/*.png | PNG | 图表图片（嵌入报表） |
