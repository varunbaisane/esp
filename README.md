# Engineering Support Escalation Platform (L1-L3)

## Purpose
This project is an Engineering Support Escalation Platform designed to manage and route support tickets across L1, L2, and L3 engineering tiers. It aims to streamline escalation workflows, track SLAs, and integrate AI for triage assistance.

## Architecture Overview
The system follows a domain-oriented modular monolith architecture that separates API, service, repository, and domain concerns while maintaining a single deployable application.
- **Backend**: Python-based API providing robust domain boundaries, service layers, and repository patterns.
- **Frontend**: React-based SPA focusing on functional UI components and feature-driven design.
- **Data Layer**: Relational database (PostgreSQL) managed via SQLAlchemy and Alembic migrations.
