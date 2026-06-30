"""
Ticket Catalog — 75 unique, realistic engineering support issues.

Each entry defines title, category, priority, and support_level.
The seed script picks 55 of these deterministically.
"""

from app.models.ticket import TicketPriority, TicketLevel

TICKET_CATALOG = [
    # ─── Authentication (8) ────────────────────
    {"title": "OAuth callback returns HTTP 500 after Azure AD login", "category": "Authentication", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L2},
    {"title": "SAML assertion validation fails silently for federated users", "category": "Authentication", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "JWT refresh token rotation leaking expired tokens to client", "category": "Authentication", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "MFA enrollment wizard not rendering on Safari 17", "category": "Authentication", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Password reset email contains malformed callback URL", "category": "Authentication", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "SSO session cookie not honoring SameSite=Strict policy", "category": "Authentication", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Login rate limiter incorrectly blocking valid users after password change", "category": "Authentication", "priority": TicketPriority.HIGH, "level": TicketLevel.L1},
    {"title": "OTP delivery delay exceeds 60 seconds during peak hours", "category": "Authentication", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},

    # ─── Backend API (9) ──────────────────────
    {"title": "REST endpoint /api/tickets returns 502 under concurrent load", "category": "Backend API", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L2},
    {"title": "Pagination offset parameter silently ignored on /api/audit-logs", "category": "Backend API", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "CORS preflight rejected for custom X-Request-ID header", "category": "Backend API", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Bulk ticket update endpoint exceeds 30-second timeout", "category": "Backend API", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Rate limiter returns 429 with missing Retry-After header", "category": "Backend API", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Webhook delivery retries exhausting connection pool", "category": "Backend API", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "API response times spiking to 8s during database migrations", "category": "Backend API", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "GraphQL query depth limiter not enforced on nested ticket relations", "category": "Backend API", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L2},
    {"title": "Health check endpoint not reporting degraded database state", "category": "Backend API", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},

    # ─── Frontend (10) ─────────────────────────
    {"title": "Dashboard widgets fail to render after session refresh", "category": "Frontend", "priority": TicketPriority.HIGH, "level": TicketLevel.L1},
    {"title": "Ticket search input loses focus on every keystroke in Firefox", "category": "Frontend", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Priority dropdown not reflecting saved value on ticket edit page", "category": "Frontend", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Stale data displayed on Team Operations after browser back navigation", "category": "Frontend", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Analytics charts render blank when dataset exceeds 500 entries", "category": "Frontend", "priority": TicketPriority.HIGH, "level": TicketLevel.L1},
    {"title": "Mobile hamburger menu overlaps ticket detail content", "category": "Frontend", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Toast notification z-index conflict with modal dialogs", "category": "Frontend", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Sidebar collapse animation jitters on low-end Chromebooks", "category": "Frontend", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Dark mode toggle does not persist across page reloads", "category": "Frontend", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Infinite scroll on activity feed triggers duplicate API calls", "category": "Frontend", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},

    # ─── Database (8) ──────────────────────────
    {"title": "PostgreSQL connection pool exhaustion during peak traffic", "category": "Database", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "Slow query on tickets table causing dashboard timeout", "category": "Database", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Missing index on audit_logs.created_at degrading activity feed", "category": "Database", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L2},
    {"title": "Dead tuples accumulating on users table after bulk imports", "category": "Database", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Database replication lag exceeding 15 seconds on read replica", "category": "Database", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "Schema migration 047 fails on PostgreSQL 15 with enum conflict", "category": "Database", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Connection leak in long-running background worker", "category": "Database", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Foreign key constraint violation when deleting archived tickets", "category": "Database", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},

    # ─── Infrastructure (8) ────────────────────
    {"title": "Kubernetes ingress intermittently returning 502 Bad Gateway", "category": "Infrastructure", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "Pod memory limit exceeded causing OOMKilled restarts", "category": "Infrastructure", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Horizontal pod autoscaler not scaling down after traffic spike", "category": "Infrastructure", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L2},
    {"title": "TLS certificate renewal failing on wildcard domain", "category": "Infrastructure", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Load balancer health checks timing out on slow startup pods", "category": "Infrastructure", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Persistent volume claim stuck in Pending state after node drain", "category": "Infrastructure", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "CDN cache invalidation not propagating for static assets", "category": "Infrastructure", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "DNS TTL misconfiguration causing intermittent resolution failures", "category": "Infrastructure", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},

    # ─── DevOps (8) ────────────────────────────
    {"title": "CI pipeline fails on ARM64 build step after Docker upgrade", "category": "DevOps", "priority": TicketPriority.HIGH, "level": TicketLevel.L1},
    {"title": "GitHub Actions workflow timeout on large monorepo checkout", "category": "DevOps", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Terraform state lock not releasing after failed apply", "category": "DevOps", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Docker image layer caching broken after registry migration", "category": "DevOps", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Staging environment drift from production Kubernetes manifests", "category": "DevOps", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Helm chart values override not applying on rolling update", "category": "DevOps", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Build artifact retention policy exceeding storage quota", "category": "DevOps", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "Secrets rotation script failing silently for Vault-managed keys", "category": "DevOps", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},

    # ─── Performance (8) ──────────────────────
    {"title": "Ticket search latency exceeds SLA under concurrent load", "category": "Performance", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Redis cache serving stale ticket metadata after priority update", "category": "Performance", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L2},
    {"title": "Background worker retry loop generating duplicate notifications", "category": "Performance", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Memory leak in WebSocket connection handler after 72 hours", "category": "Performance", "priority": TicketPriority.HIGH, "level": TicketLevel.L3},
    {"title": "Audit log query N+1 problem causing 12-second page loads", "category": "Performance", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "CSV export of 10K tickets consuming 2GB of server memory", "category": "Performance", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Gunicorn worker timeout under sustained 200 req/s load", "category": "Performance", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "Frontend bundle size regression causing 4s LCP on mobile", "category": "Performance", "priority": TicketPriority.LOW, "level": TicketLevel.L1},

    # ─── Security (8) ──────────────────────────
    {"title": "XSS vulnerability in ticket description markdown renderer", "category": "Security", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "IDOR vulnerability allows reading other users' ticket comments", "category": "Security", "priority": TicketPriority.HIGH, "level": TicketLevel.L3},
    {"title": "Content-Security-Policy header missing on API error responses", "category": "Security", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Audit log entries not redacting PII in event_metadata field", "category": "Security", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Session tokens not invalidated on password change", "category": "Security", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "RBAC bypass when accessing admin endpoints via URL manipulation", "category": "Security", "priority": TicketPriority.CRITICAL, "level": TicketLevel.L3},
    {"title": "Dependency vulnerability CVE-2025-1234 in axios 1.6.x", "category": "Security", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "API key exposed in client-side JavaScript bundle", "category": "Security", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},

    # ─── Integrations (8) ─────────────────────
    {"title": "Email verification delayed due to SMTP timeout on SendGrid", "category": "Integrations", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Slack notification webhook returning 403 after token rotation", "category": "Integrations", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Jira bi-directional sync creating duplicate tickets", "category": "Integrations", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "PagerDuty alert routing sending all incidents to wrong team", "category": "Integrations", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
    {"title": "Datadog metrics agent dropping custom tags after pod restart", "category": "Integrations", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "GitHub commit status checks not updating on protected branches", "category": "Integrations", "priority": TicketPriority.MEDIUM, "level": TicketLevel.L1},
    {"title": "Sentry error grouping merging distinct exceptions", "category": "Integrations", "priority": TicketPriority.LOW, "level": TicketLevel.L1},
    {"title": "AWS SES bounce rate approaching account suspension threshold", "category": "Integrations", "priority": TicketPriority.HIGH, "level": TicketLevel.L2},
]
