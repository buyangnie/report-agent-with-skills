# Data Contract - BO Workload Performance Report

## Data Source
**File**: `data/Incidents-exported.xlsx`

## Required Sheets

### Sheet 1: SLA_Criteria
| Field | Type | Description |
|-------|------|-------------|
| Priority | Text | P1/P2/P3/P4 |
| Response (minutes) | Number | Response time SLA |
| Resolution (hours) | Number | Resolution time SLA |

### Sheet 2: Data
| Field | Type | Description | Used For |
|-------|------|-------------|----------|
| Order Number | Text | Ticket unique ID | Identification |
| Order Name | Text | Ticket title/description | Keyword analysis |
| Begin Date | DateTime | Created time | Time analysis |
| Resolution Date | DateTime | Resolved time | MTTR calculation |
| Resolver | Text | Handler name | **Core: Expert identification** |
| Category | Text | Incident category | **Core: Specialty analysis** |
| Priority | Text | P1/P2/P3/P4 | **Core: Tier identification** |
| Resolution Time(m) | Number | Resolution duration (minutes) | **Core: Efficiency** |
| Response Time(m) | Number | Response duration (minutes) | Efficiency |
| Current Phase | Text | Current phase | Backlog detection |
| Order Status | Text | Ticket status | Backlog detection |

## Computed Fields

| Field | Formula | Purpose |
|-------|---------|---------|
| Resolution_Hours | Resolution Time(m) / 60 | MTTR in hours |
| SLA_Res_Violated | Boolean | SLA compliance check |
| Is_BO_Ticket | Boolean | Based on Priority/Category rules |
| Complexity_Score | Normalized MTTR | Complexity indicator |

## Data Quality Requirements

### Required Fields (must not be null)
- Order Number
- Begin Date
- Resolver
- Category
- Priority

### Filtering Rules
- Exclude: Resolver = "Unassigned" or "System"
- Exclude: Resolution Time(m) < 0
