# Engineering Support Escalation Platform (ESP)

![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Field](https://img.shields.io/badge/Field-Engineering_Operations-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)

A full-stack engineering operations platform that models real-world support workflows across L1, L2, and L3 teams with workflow enforcement, SLA management, audit logging, assignment ownership, RBAC, operational dashboards, and analytics.


**Key Highlights**:
- Enforced escalation workflows and state-machine transitions.
- Priority-driven SLA tracking and real-time breach detection.
- Immutable, tamper-evident audit trails for all critical actions.
- Role-based operational dashboards and analytics for engineering managers.

| Area | Features |
|--------|----------|
| Authentication | JWT Authentication, Registration, Protected Routes |
| Authorization | RBAC, Tier-Based Escalation Permissions |
| Ticketing | Creation, Assignment, Claiming, Ownership |
| Workflow | State Machine, Escalation Engine |
| SLA | Deadline Tracking, Breach Detection |
| Auditability | Immutable Audit Logs, Activity Center |
| Operations | Workspace, Team Operations Dashboard |
| Analytics | SLA Compliance, Resolution Metrics, Workload Distribution |

---

## Screenshots

![Login](docs/screenshots/login.png)

![My Workspace](docs/screenshots/workspace1.png)

![My Workspace](docs/screenshots/workspace2.png)

![Ticket Explorer](docs/screenshots/ticket-explorer.png)

![Ticket Detail](docs/screenshots/ticket-detail.png)

![Activity Center](docs/screenshots/activity-center.png)

![Team Operations](docs/screenshots/team-operations.png)

![Analytics](docs/screenshots/analytics.png)

---

## Architecture Overview

ESP utilizes a robust, decoupled architecture separating the frontend presentation layer from a scalable backend REST API.

### High-Level Architecture

```text
ESP Platform
├── React Frontend
└── FastAPI API
    ├── Core Modules
    │   ├── Authentication
    │   ├── RBAC
    │   ├── SLA Engine
    │   └── Audit Engine
    └── Data Pipeline
        ├── Service Layer
        ├── Repository Layer
        └── PostgreSQL Database
```

### Escalation Workflow

Tickets flow deterministically through defined support tiers. Engineers can only escalate tickets if they have the necessary permissions.

```text
Escalation Path
├── L1 Support (Triage & Standard)
│   └── Escalates to
├── L2 Support (Advanced Triage)
│   └── Escalates to
└── L3 Support (Engineering/Dev)
```

### Ticket Lifecycle

A strict state machine governs ticket lifecycles, ensuring tickets cannot transition into invalid states.

```text
Ticket Lifecycle
├── OPEN
│   └── Assign / Claim
├── IN_PROGRESS
│   ├── Resolve Issue
│   │   └── RESOLVED
│   └── Unassign / Reopen
│       └── OPEN
└── RESOLVED
    └── Verify & Close
        └── CLOSED
```

---

## Core Features

### Authentication & Authorization
- **JWT Authentication**: Secure, stateless session management.
- **Protected Routes**: UI components and API endpoints restricted based on authentication status.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions separating `ADMIN`, `ENGINEERING_MANAGER`, and tiered `SUPPORT_L1/L2/L3` roles.

### Ticket Management
- **Ticket Creation & Assignment**: Strict creation workflows and assignment rules.
- **Ticket Ownership**: Claiming mechanisms to lock ticket resolution to specific engineers.
- **Ticket Explorer**: Advanced filtering (by status, priority, SLA, assignee), sorting, and pagination.

### Workflow Engine
- **State Machine**: Enforces valid status transitions.
- **Escalation Engine**: Deterministic promotion of tickets across support tiers (L1 → L2 → L3).

### SLA Engine
- **Priority-Driven SLAs**: Deadlines computed dynamically based on Ticket Priority (Low, Medium, High, Critical).
- **SLA Breach Detection**: Automated flagging of At-Risk and Breached tickets.

### Audit & Activity
- **Immutable Audit Logs**: Tracking every mutation (status change, reassignment, escalation) with metadata.
- **Activity Center**: A global timeline view of all platform operations.
- **Ticket Timelines**: Granular history views on individual tickets.

### Operations Dashboards
- **Personal Workspace**: Curated views for individual engineers focusing on assigned workloads.
- **Team Operations**: Managerial views into tier-specific active tickets, unassigned queues, and breaches.
- **Global Operations**: High-level platform health summaries.
- **Analytics**: Real-time reporting on SLA compliance, resolution times, workload distributions, and escalation frequencies.

---

## Technology Stack

**Backend**:
- **Framework**: FastAPI
- **Database ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Database**: PostgreSQL
- **Data Validation**: Pydantic

**Frontend**:
- **Framework**: React (Vite)
- **Language**: TypeScript
- **HTTP Client**: Axios
- **Styling**: TailwindCSS
- **Data Visualization**: Recharts

**Infrastructure**:
- **Containerization**: Docker & Docker Compose

---

## Project Structure

```text
engineering-support-platform
├── backend
│   ├── app
│   │   ├── api          # FastAPI route handlers
│   │   ├── core         # Config and security
│   │   ├── db           # Database connection and sessions
│   │   ├── models       # SQLAlchemy ORM models
│   │   ├── repositories # Data access layer
│   │   ├── schemas      # Pydantic validation models
│   │   └── services     # Business logic
│   ├── migrations       # Alembic migrations
│   └── scripts          # Database seeding scripts
├── frontend
│   ├── public           # Static assets
│   └── src
│       ├── components   # Reusable UI components
│       ├── context      # React context providers
│       ├── hooks        # Custom React hooks
│       ├── pages        # Top-level page components
│       ├── services     # API client functions
│       └── types        # TypeScript interfaces
└── docker-compose.yml   # Docker configuration
```

---

## Database ER Diagram

```text
Database Schema
├── USERS
│   ├── id (PK)
│   ├── email
│   ├── full_name
│   └── hashed_password
├── ROLES
│   ├── id (PK)
│   └── name
├── USER_ROLES (Join Table)
│   ├── user_id (FK -> USERS)
│   └── role_id (FK -> ROLES)
├── TICKETS
│   ├── id (PK)
│   ├── title
│   ├── description
│   ├── status
│   ├── priority
│   ├── support_level
│   ├── sla_due_at
│   ├── closed_at
│   ├── created_by_id (FK -> USERS)
│   └── assigned_to_id (FK -> USERS)
└── AUDIT_LOGS
    ├── id (PK)
    ├── action
    ├── entity_type
    ├── entity_id
    ├── event_metadata (JSON)
    ├── actor_id (FK -> USERS)
    └── ticket_id (FK -> TICKETS)
```

---

## Demo Organization

The platform comes with a comprehensive seed script that provisions a realistic engineering organization. 

**Default Password for all accounts**: `Password123!`

### Administrative & Managerial
- `admin@esp.local` (Admin User)
- `manager@esp.local` (Engineering Manager)

### L1 Support Engineers
- `alice.l1@esp.local` (Alice Johnson)
- `john.l1@esp.local` (John Doe)
- `sarah.l1@esp.local` (Sarah Connor)

### L2 Support Engineers
- `bob.l2@esp.local` (Bob Smith)
- `mike.l2@esp.local` (Mike Wazowski)

### L3 Support Engineers
- `charlie.l3@esp.local` (Charlie Brown)
- `david.l3@esp.local` (David Wallace)

---

## Demo Workflow

To experience the platform's escalation enforcement:

1. **Create an Issue**: Log in as `alice.l1@esp.local` and create a high-priority ticket. 
2. **Claim & Escalate**: Claim the ticket as Alice, realize it requires deeper investigation, and use the "Escalate" action to send it to the L2 queue.
3. **L2 Triage**: Log out and log back in as `bob.l2@esp.local`. Navigate to Team Operations to see the newly escalated ticket in the L2 unassigned queue.
4. **Resolution**: Bob claims the ticket, investigates, and changes the status to `Resolved`.
5. **Audit Trail**: Log in as `manager@esp.local` and view the Ticket Timeline or global Activity Center to see the complete immutable history of Alice's creation/escalation and Bob's resolution.

---

## Installation

### Prerequisites
- Docker and Docker Compose
- Node.js (v18+)
- Python 3.10+
- Poetry

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/engineering-support-platform.git
cd engineering-support-platform
```

### 2. Database Setup
Start the PostgreSQL container:
```bash
docker-compose up -d db
```

### 3. Backend Setup
```bash
cd backend
poetry install
cp .env.example .env
```

Apply database migrations:
```bash
poetry run alembic upgrade head
```

Seed the database with the demo organization:
```bash
poetry run python scripts/seed_demo_data.py
```

Start the backend server:
```bash
poetry run uvicorn app.main:app --reload
```

### 4. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
The application will be available at `http://localhost:5173`.

---

## API Documentation

Detailed documentation and interactive consoles are available for the backend API:

- **API Reference**: [docs/api.md](docs/api.md)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Future Enhancements

While ESP is fully functional, future iterations may include:
- **Notifications**: Real-time WebSocket notifications and Slack/Email integrations.
- **Saved Views**: User-configurable ticket filter presets.
- **Advanced Analytics**: Trend lines, forecasting, and historical capacity planning.
- **Scheduled Reports**: Automated PDF/CSV exports of SLA metrics sent to engineering managers.

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.
