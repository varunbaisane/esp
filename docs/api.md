# Engineering Support Escalation Platform (ESP)

# API Reference

This document provides a concise developer-facing reference for the major endpoints of the Engineering Support Escalation Platform (ESP). It focuses on operational behavior, escalation workflows, and state transitions.

For exhaustive OpenAPI schema generation (including all request payloads and response models), please consult the interactive documentation interfaces provided by the backend.

---

## Base URL

All endpoints are prefixed with:

```http
/api/v1
```

---

## Endpoint Summary

| Domain | Endpoints |
|----------|----------|
| Auth | Register, Login, Current User |
| Users | List Users |
| Tickets | CRUD, Claim, Assign, Escalate |
| Audit | Activity Feed, Ticket Timeline |
| Workspace | Personal Workspace |
| Team Operations | Queue Management |
| Analytics | Operational Reporting |

---

## Authentication

### Register

```http
POST /api/v1/auth/register
```

**Purpose**: Create a new account in the ESP platform.

**Example Request**:
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "Password123!",
  "confirmPassword": "Password123!"
}
```

### Login

```http
POST /api/v1/auth/login
```

**Purpose**: Authenticate an existing user and retrieve a JWT token.

**Returns**:
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Current User

```http
GET /api/v1/auth/me
```

**Purpose**: Returns the authenticated user's details and active role assignments.

---

## Users

### List Users

```http
GET /api/v1/users
```

**Purpose**: Retrieve available engineers and platform users.

---

## Tickets

### Create Ticket

```http
POST /api/v1/tickets
```

**Purpose**: Creates a new support ticket.
Requires standard metadata:
- `title`
- `description`
- `priority`

**Automated Operations**:
- Assigns Level `L1` support automatically.
- Calculates SLA deadlines based on the assigned priority.
- Generates an immutable audit event for the creation.

### List Tickets

```http
GET /api/v1/tickets
```

**Purpose**: Search, filter, and paginate through tickets across the platform.

**Supported Filters**:
- `status`
- `priority`
- `level`
- `assigned_to`
- `sla_status`

**Supported Sorting**:
- `created_at`
- `priority`
- `level`
- `status`
- `sla_due_at`

**Supported Pagination**:
- `limit` (Default: 25)
- `offset` (Default: 0)

### Ticket Details

```http
GET /api/v1/tickets/{id}
```

**Purpose**: Retrieve full details and metadata for a specific ticket.

### Update Ticket

```http
PATCH /api/v1/tickets/{id}
```

**Purpose**: Execute workflow-safe updates (e.g., status changes, re-prioritization).

### Claim Ticket

```http
POST /api/v1/tickets/{id}/claim
```

**Requirements**:
- The user must have sufficient support tier permissions (`L1`, `L2`, or `L3`) matching the ticket's current required tier.

### Assign Ticket

```http
POST /api/v1/tickets/{id}/assign
```

**Requirements**:
- Assignment permissions are validated through RBAC.
- Users may only assign tickets within their permitted support scope.
- `ENGINEERING_MANAGER` and `ADMIN` may assign across all support tiers.

### Escalate Ticket

```http
POST /api/v1/tickets/{id}/escalate
```

**Workflow Path**:
`L1` → `L2` → `L3`

**Constraints**:
Tickets can only be escalated to the next logical support tier. Invalid escalations will be rejected by the backend state machine, returning either:
- `400 Bad Request`
- `403 Forbidden`

---

## Audit

### Recent Activity

```http
GET /api/v1/audit/recent
```

**Purpose**: Returns the most recent system-wide audit events.

### Ticket Timeline

```http
GET /api/v1/tickets/{id}/audit
```

**Purpose**: Returns the full, immutable history and timeline of state changes for a single ticket.

### Activity Center

```http
GET /api/v1/audit
```

**Purpose**: Returns a paginated activity feed across the entire platform. Supports `limit` (Default: 25) and `offset` (Default: 0).

---

## Workspace

### Personal Workspace

```http
GET /api/v1/workspace
```

**Purpose**: Provide a personalized view for an individual engineer.
**Returns**:
- Personal SLA metrics
- The user's explicitly assigned ticket queue

---

## Team Operations

### Team Operations Dashboard

```http
GET /api/v1/team-operations
```

**RBAC Requirements**:
- `ADMIN`
- `ENGINEERING_MANAGER`

**Provides**:
- Queue depth metrics across tiers
- Global unassigned tickets
- Actively breached SLA tickets
- Current engineer workload distributions

---

## Analytics

### Analytics Dashboard

```http
GET /api/v1/analytics
```

**RBAC Requirements**:
- `ADMIN`
- `ENGINEERING_MANAGER`

**Provides**:
- Ticket volume distributions
- SLA compliance health
- Mean Time to Resolution (MTTR) metrics
- Escalation frequency metrics
- Historical workload analytics

---

## Authentication Header

Secure endpoints require a standard Bearer token header obtained from the Login endpoint.

**Example**:
```http
Authorization: Bearer <access_token>
```

---

## Error Responses

The ESP backend strictly enforces operations and returns standardized error payloads.

### 400 Bad Request

**Cause**: Workflow violation or state machine error.
**Example**:
```json
{
  "detail": "Invalid status transition"
}
```

### 401 Unauthorized

**Cause**: Missing, expired, or invalid JWT token.

### 403 Forbidden

**Cause**: RBAC restriction (e.g., L1 user attempting to execute a managerial action).
**Example**:
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found

**Cause**: The requested resource (ticket, user, etc.) does not exist.

---

## Workflow Guarantees

ESP enforces several platform-wide invariants:

- Invalid status transitions are rejected.
- Escalations follow L1 → L2 → L3 only.
- RBAC is enforced on all mutation endpoints.
- SLA deadlines are generated automatically.
- Escalations reset ownership to the destination queue.
- All critical actions generate immutable audit events.

---

## OpenAPI Documentation

While the backend is running locally, you can access the automatically generated OpenAPI specs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Notes

This document intentionally focuses on operational behavior and workflow semantics rather than exhaustive schema generation. For complete request/response models, parameter constraints, and schemas, please consult the live Swagger UI.
