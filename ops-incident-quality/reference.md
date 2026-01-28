# Data Contract

## Input File
- **Format:** Excel (`.xlsx`)
- **Location:** `data/` directory (first `.xlsx` file found)
- **Encoding:** UTF-8 recommended

## Sheet 1: `SLA_Criteria`
Defines SLA targets for each priority level.

| Field | Type | Example | Description |
|---|---|---|---|
| Priority | Text | P1, P2, P3, P4 | Priority level identifier |
| Response (minutes) | Number | 15 | Response time target in minutes |
| Resolution (hours) | Number | 4 | Resolution time target in hours |

## Sheet 2: `Data`
Raw incident/ticket data.

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| Order Number | Text | ✓ | INC001234 | Unique ticket identifier |
| Order Name | Text | ✓ | Server down | Ticket title/summary |
| Begin Date | DateTime | ✓ | 2024-06-15 10:30 | Ticket creation timestamp |
| Resolution Date | DateTime | ✓ | 2024-06-15 14:45 | Ticket resolution timestamp |
| Resolver | Text | ✓ | john.doe | Assignee/resolver name |
| Category | Text | ✓ | Network | Incident category |
| Priority | Text | ✓ | P1, P2, P3, P4 | Priority level |
| Resolution Time(m) | Number | ✓ | 255 | Total resolution time in minutes |
| Response Time(m) | Number | ✓ | 12 | Initial response time in minutes |
| Suspend Time(m) | Number | Optional | 60 | Suspended/paused duration |

## Data Cleaning Rules
The analysis engine automatically handles:

1. **Empty Resolver** → Marked as "Unassigned"
2. **Negative Resolution Time** → Excluded from MTTR calculations
3. **Invalid Date Format** → Error and abort with message
4. **Missing Priority** → Defaults to "P4"
5. **Whitespace in text fields** → Automatically trimmed

## Calculated Fields
The engine adds these computed columns:

| Field | Formula | Description |
|---|---|---|
| Resolution_Hours | Resolution Time(m) / 60 | Resolution time in hours |
| SLA_Met | Compare against SLA_Criteria | Boolean: met SLA target |
| Period | Based on date range midpoint | "Current" or "Previous" |
| DayOfWeek | From Begin Date | 0=Monday, 6=Sunday |
| Hour | From Begin Date | 0-23 hour of day |

## Output Files
Generated in `output/` directory:

| File | Format | Description |
|---|---|---|
| Deep_Dive_Report.html | HTML | Web-based flowing document |
| Deep_Dive_Report.docx | DOCX | Editable Word document |
| Deep_Dive_Report.pptx | PPTX | 16:9 PowerPoint presentation |
| images/*.png | PNG | Chart images (embedded in reports) |
