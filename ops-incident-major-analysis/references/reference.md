# Data Contract

## Input Format

This skill expects incident data in JSON format. The data can be provided via:
1. A JSON file in the `data/` directory
2. Direct input through the skill interface
3. API integration (project-specific adapter)

---

## JSON Schema

### Root Object

```json
{
  "incident": { ... },
  "timeline": [ ... ]
}
```

### Incident Object (Required)

| Field | Type | Required | Example | Description |
|-------|------|----------|---------|-------------|
| order_number | string | ✓ | "80000001" | Unique identifier |
| title | string | ✓ | "Payment gateway timeout" | Incident title/summary |
| priority | string | ✓ | "P1" | Priority level (P1/P2/P3/P4) |
| category | string | ✓ | "Network" | Incident category |
| status | string | ✓ | "In Progress" | Current status |
| created_at | datetime | ✓ | "2025-01-15T10:30:00" | Creation timestamp (ISO 8601) |
| resolved_at | datetime | | "2025-01-15T14:30:00" | Resolution timestamp (null if ongoing) |
| affected_systems | array | | ["Payment", "Order"] | List of affected systems |
| sla.response_minutes | number | ✓ | 15 | SLA response time target |
| sla.resolution_hours | number | ✓ | 2 | SLA resolution time target |

### Timeline Array (Required)

Each timeline event represents an action or state change in the incident lifecycle.

| Field | Type | Required | Example | Description |
|-------|------|----------|---------|-------------|
| timestamp | datetime | ✓ | "2025-01-15T10:30:00" | Event timestamp (ISO 8601) |
| event | string | ✓ | "status_change" | Event type (see below) |
| actor | string | ✓ | "John Smith" | Person/system performing action |
| from | string | | "Open" | Previous value (for changes) |
| to | string | | "In Progress" | New value (for changes) |
| detail | string | | "Started diagnosis" | Additional context |

### Event Types

| Event Type | Description | Expected Fields |
|------------|-------------|-----------------|
| `created` | Incident created | actor, detail |
| `assigned` | Assigned to person/team | actor, from, to |
| `reassigned` | Reassigned to different person | actor, from, to |
| `escalated` | Escalated to higher level | actor, from, to |
| `status_change` | Status changed | actor, from, to |
| `priority_change` | Priority changed | actor, from, to |
| `note` | Note/comment added | actor, detail |
| `resolved` | Incident resolved | actor, detail |
| `closed` | Incident closed | actor, detail |
| `reopened` | Incident reopened | actor, detail |

---

## Example Input

```json
{
  "incident": {
    "order_number": "80000001",
    "title": "Payment gateway timeout causing transaction failures",
    "priority": "P1",
    "category": "Network",
    "status": "Resolved",
    "created_at": "2025-01-15T10:30:00",
    "resolved_at": "2025-01-15T14:45:00",
    "affected_systems": ["Payment Gateway", "Order Service", "Mobile App"],
    "sla": {
      "response_minutes": 15,
      "resolution_hours": 2
    }
  },
  "timeline": [
    {
      "timestamp": "2025-01-15T10:30:00",
      "event": "created",
      "actor": "Monitoring System",
      "detail": "Auto-created from alert: Payment API response time > 5s"
    },
    {
      "timestamp": "2025-01-15T10:32:00",
      "event": "assigned",
      "actor": "Auto Dispatcher",
      "from": null,
      "to": "John Smith",
      "detail": "Assigned based on rotation schedule"
    },
    {
      "timestamp": "2025-01-15T10:35:00",
      "event": "status_change",
      "actor": "John Smith",
      "from": "Open",
      "to": "In Progress",
      "detail": "Acknowledged, starting diagnosis"
    },
    {
      "timestamp": "2025-01-15T10:50:00",
      "event": "note",
      "actor": "John Smith",
      "detail": "Initial diagnosis: Connection pool exhaustion suspected"
    },
    {
      "timestamp": "2025-01-15T11:00:00",
      "event": "escalated",
      "actor": "John Smith",
      "from": "L1 Support",
      "to": "L2 Database Team",
      "detail": "Need DBA expertise for connection pool tuning"
    },
    {
      "timestamp": "2025-01-15T11:15:00",
      "event": "assigned",
      "actor": "L2 Dispatcher",
      "from": "John Smith",
      "to": "Database Expert Team",
      "detail": null
    },
    {
      "timestamp": "2025-01-15T11:45:00",
      "event": "note",
      "actor": "Mary Johnson",
      "detail": "Confirmed: Connection leak in payment service v2.3.1"
    },
    {
      "timestamp": "2025-01-15T12:30:00",
      "event": "note",
      "actor": "Mary Johnson",
      "detail": "Hotfix deployed, monitoring recovery"
    },
    {
      "timestamp": "2025-01-15T14:30:00",
      "event": "resolved",
      "actor": "Mary Johnson",
      "detail": "Service recovered, connection pool stable for 2 hours"
    },
    {
      "timestamp": "2025-01-15T14:45:00",
      "event": "closed",
      "actor": "John Smith",
      "detail": "Verified with business team, closing ticket"
    }
  ]
}
```

---

## Validation Rules

The analyzer will validate:

1. **Required Fields**: All required fields must be present
2. **Timeline Order**: Events must be in chronological order
3. **Timestamp Format**: Must be valid ISO 8601 datetime
4. **Event Types**: Must be one of the defined event types
5. **Priority Values**: Must be P1, P2, P3, or P4
6. **SLA Values**: Must be positive numbers

### Error Handling

| Error | Behavior |
|-------|----------|
| Missing required field | Abort with error message |
| Invalid timestamp | Abort with error message |
| Empty timeline | Warning, limited analysis |
| Unknown event type | Warning, treated as "note" |

---

## Output Files

Generated in `output/` directory:

| File | Format | Description |
|------|--------|-------------|
| `Major_Incident_Analysis_{order_number}_{lang}.html` | HTML | Interactive web report |
| `Major_Incident_Analysis_{order_number}_{lang}.docx` | DOCX | Formal document |
| `images/*.png` | PNG | Embedded chart images |
