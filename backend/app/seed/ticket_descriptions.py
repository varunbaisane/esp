"""
Ticket Descriptions — Structured, enterprise-quality descriptions.

Generates markdown descriptions with:
  - Summary
  - Business Impact
  - Observed Behaviour
  - Expected Behaviour
  - Reproduction Steps
  - Additional Notes

Descriptions are keyed by ticket title for deterministic lookup.
"""

# Map of ticket title -> structured markdown description
# For titles not explicitly listed, a generic generator is used.

TICKET_DESCRIPTIONS: dict[str, str] = {
    "OAuth callback returns HTTP 500 after Azure AD login": """## Summary
OAuth callback endpoint throws an unhandled exception after Azure AD returns the authorization code.

## Business Impact
All Azure AD SSO users are unable to authenticate. Approximately 340 users affected across 3 departments.

## Observed Behaviour
After clicking "Sign in with Azure AD", users are redirected to `/auth/callback` which returns HTTP 500 with a generic error page.

## Expected Behaviour
Users should be authenticated and redirected to their dashboard.

## Reproduction Steps
1. Navigate to `/login`
2. Click "Sign in with Azure AD"
3. Complete Azure AD authentication
4. Observe 500 error on callback

## Additional Notes
Error logs show `KeyError: 'id_token'` in the OIDC handler. Possibly related to the Azure AD library upgrade in v2.4.1.""",

    "PostgreSQL connection pool exhaustion during peak traffic": """## Summary
Database connection pool reaches maximum capacity during morning peak (09:00–10:30 UTC), causing cascading failures across all API endpoints.

## Business Impact
Complete platform unavailability for 15–45 minutes during peak hours. 800+ engineers unable to create or update tickets.

## Observed Behaviour
API returns HTTP 503 with `QueuePool limit of 20 overflow 10 reached` error. All subsequent requests queue and timeout.

## Expected Behaviour
Connection pool should handle peak traffic gracefully with proper connection recycling and overflow management.

## Reproduction Steps
1. Generate 50 concurrent API requests using `ab -n 1000 -c 50`
2. Monitor `pg_stat_activity` for active connections
3. Observe pool exhaustion after ~30 seconds of sustained load

## Additional Notes
Current pool configuration: `pool_size=20, max_overflow=10, pool_timeout=30`. May need to increase or add PgBouncer.""",

    "Redis cache serving stale ticket metadata after priority update": """## Summary
After updating a ticket's priority, the Redis cache continues serving the old priority value for up to 5 minutes.

## Business Impact
Engineers see incorrect priority levels in the ticket list, leading to misallocation of resources. Two P1 incidents were triaged as P3 due to stale cache data.

## Observed Behaviour
PUT `/api/tickets/42` updates priority to CRITICAL successfully (confirmed in DB), but GET `/api/tickets/42` returns MEDIUM for 3–5 minutes.

## Expected Behaviour
Cache should be invalidated immediately on any ticket mutation.

## Reproduction Steps
1. Note current priority of any ticket
2. Update priority via API or UI
3. Immediately refresh the ticket list
4. Observe stale priority value

## Additional Notes
Cache invalidation logic exists but only fires on status changes, not priority changes. Likely a missing invalidation trigger.""",

    "Kubernetes ingress intermittently returning 502 Bad Gateway": """## Summary
NGINX ingress controller returns 502 errors for approximately 2–5% of requests during pod rolling updates.

## Business Impact
Users experience intermittent errors during deployments. Customer-facing SLA of 99.9% uptime is at risk.

## Observed Behaviour
During rolling deployments, some requests hit pods that are terminating, resulting in 502 responses.

## Expected Behaviour
Rolling updates should be zero-downtime with proper readiness probe configuration and connection draining.

## Reproduction Steps
1. Trigger a rolling deployment via `kubectl rollout restart`
2. Run continuous health checks: `while true; do curl -s -o /dev/null -w "%{http_code}" https://api.esp.internal; done`
3. Observe 502 errors during the transition window

## Additional Notes
Pre-stop hook and terminationGracePeriodSeconds may need adjustment. Consider adding a readiness gate.""",

    "Email verification delayed due to SMTP timeout on SendGrid": """## Summary
Email verification OTPs are delivered 45–90 seconds after registration, exceeding the expected 5-second delivery window.

## Business Impact
New user onboarding experience is degraded. Support team receives 20+ complaints per day about delayed verification emails.

## Observed Behaviour
Emails are queued successfully but SendGrid API responds with 202 after 30+ seconds instead of the usual sub-second response.

## Expected Behaviour
OTP emails should be delivered within 5 seconds of registration.

## Reproduction Steps
1. Register a new account via `/register`
2. Monitor SendGrid delivery timestamps in the admin dashboard
3. Observe 45–90 second delay between API call and delivery

## Additional Notes
SendGrid status page shows no incidents. Possibly related to DNS resolution latency from the backend container.""",

    "Ticket search latency exceeds SLA under concurrent load": """## Summary
Full-text search on the tickets endpoint degrades to 8–12 second response times when more than 20 concurrent search queries are active.

## Business Impact
Engineers report that the ticket search is "unusable" during standup hours (09:00–10:00). Productivity loss estimated at 30 minutes per engineer per day.

## Observed Behaviour
GET `/api/tickets?search=<term>` responds in 8–12 seconds under concurrent load. Normal response time is 200ms.

## Expected Behaviour
Search queries should return within 500ms regardless of concurrent load.

## Reproduction Steps
1. Generate 20 concurrent search requests with varying terms
2. Measure p95 response time
3. Observe degradation beyond 8 seconds

## Additional Notes
PostgreSQL `pg_trgm` index may need to be replaced with a dedicated search engine (Elasticsearch or Meilisearch) for scale.""",

    "Dashboard widgets fail to render after session refresh": """## Summary
After a JWT token refresh, the dashboard page shows empty widget containers with no data loading.

## Business Impact
Users must manually hard-refresh (Ctrl+F5) to restore dashboard functionality. Affects all authenticated users after 30 minutes of inactivity.

## Observed Behaviour
Widget containers render but API calls return 401. The auth interceptor refreshes the token but does not retry the failed requests.

## Expected Behaviour
After token refresh, all pending API requests should be retried automatically.

## Reproduction Steps
1. Log in and navigate to Dashboard
2. Wait 30 minutes (token expiry)
3. Refresh the page
4. Observe empty widgets with no error messages

## Additional Notes
The Axios interceptor handles 401 and refreshes the token, but the original requests are dropped. Need to implement a request queue during refresh.""",

    "Background worker retry loop generating duplicate notifications": """## Summary
The Celery background worker enters a retry loop when notification delivery fails, generating up to 50 duplicate email notifications per failed delivery.

## Business Impact
Users receive dozens of duplicate emails for the same event. Three enterprise customers have raised formal complaints.

## Observed Behaviour
When SendGrid returns a transient 429 error, the worker retries immediately without backoff, generating duplicate delivery attempts.

## Expected Behaviour
Worker should implement exponential backoff with jitter and a maximum retry count of 3.

## Reproduction Steps
1. Temporarily block SendGrid API access (simulate 429)
2. Trigger a ticket assignment notification
3. Monitor the Celery task queue for retry attempts
4. Observe 50+ retry tasks created within 60 seconds

## Additional Notes
Max retries is currently set to `None` (unlimited). Needs to be capped at 3 with exponential backoff.""",

    "XSS vulnerability in ticket description markdown renderer": """## Summary
Malicious JavaScript can be injected via ticket descriptions using crafted markdown that bypasses the sanitizer.

## Business Impact
Critical security vulnerability. An attacker could steal session tokens from any user viewing the malicious ticket.

## Observed Behaviour
Input `![x](javascript:alert(document.cookie))` is rendered as an executable script in the browser.

## Expected Behaviour
All HTML output from the markdown renderer should be sanitized. JavaScript URIs must be stripped.

## Reproduction Steps
1. Create a ticket with description: `![x](javascript:alert(1))`
2. Navigate to the ticket detail page
3. Observe JavaScript execution

## Additional Notes
The markdown library allows raw HTML by default. Need to enable `sanitize: true` or use DOMPurify as a post-processing step.""",

    "CI pipeline fails on ARM64 build step after Docker upgrade": """## Summary
After upgrading Docker Engine from 24.x to 25.x, the multi-architecture build step fails with an exec format error on ARM64.

## Business Impact
All CI/CD deployments are blocked. Team cannot ship any code changes until the pipeline is fixed.

## Observed Behaviour
`docker buildx build --platform linux/arm64` fails with `exec /bin/sh: exec format error` during the RUN step.

## Expected Behaviour
Multi-architecture builds should complete successfully for both amd64 and arm64 targets.

## Reproduction Steps
1. Trigger CI pipeline on any branch
2. Observe failure at the "Build Docker Image" step
3. Check logs for `exec format error`

## Additional Notes
QEMU user-static binaries may need to be re-registered after the Docker upgrade. Run `docker run --privileged multiarch/qemu-user-static --reset -p yes`.""",

    "IDOR vulnerability allows reading other users' ticket comments": """## Summary
Authenticated users can read ticket comments from tickets they do not have access to by manipulating the comment ID in the API request.

## Business Impact
Confidential ticket discussions may be exposed to unauthorized users. Potential compliance violation for SOC 2 requirements.

## Observed Behaviour
GET `/api/tickets/999/comments/42` returns comment data regardless of whether the requesting user has access to ticket 999.

## Expected Behaviour
API should verify the requesting user has read access to the parent ticket before returning comment data.

## Reproduction Steps
1. Create a ticket as User A with a confidential comment
2. Log in as User B (who has no access to the ticket)
3. Send GET `/api/tickets/{ticket_id}/comments/{comment_id}`
4. Observe that the comment is returned

## Additional Notes
The comments endpoint is missing the ticket-level authorization check. All other ticket sub-resources have this check.""",

    "Memory leak in WebSocket connection handler after 72 hours": """## Summary
The WebSocket connection handler leaks approximately 50MB of memory per day, eventually causing the pod to be OOMKilled after 72 hours.

## Business Impact
Real-time notification delivery becomes unreliable. Pod restarts cause all connected clients to lose their WebSocket connections.

## Observed Behaviour
Kubernetes reports steadily increasing memory usage from 256MB to 4GB over 72 hours. Pod restarts via OOMKill.

## Expected Behaviour
Memory usage should remain stable regardless of uptime duration.

## Reproduction Steps
1. Monitor pod memory usage over 72 hours via Prometheus/Grafana
2. Observe linear growth in RSS memory
3. Profile with `memray` to identify leaked objects

## Additional Notes
Suspect that disconnected WebSocket handlers are not being garbage collected due to circular references in the event listener chain.""",

    "Database replication lag exceeding 15 seconds on read replica": """## Summary
The PostgreSQL read replica falls 15–30 seconds behind the primary during write-heavy operations, causing stale reads on the dashboard.

## Business Impact
Dashboard and analytics views show outdated data. Engineers making time-sensitive triage decisions see stale ticket statuses.

## Observed Behaviour
`pg_stat_replication.replay_lag` shows 15–30 seconds during peak write operations (bulk imports, mass ticket updates).

## Expected Behaviour
Replication lag should remain below 1 second under normal operating conditions.

## Reproduction Steps
1. Run a bulk import of 500 tickets via the admin API
2. Monitor `pg_stat_replication` on the primary
3. Observe replay_lag exceeding 15 seconds

## Additional Notes
WAL sender configuration may need tuning. Consider increasing `wal_sender_timeout` and `max_wal_senders`.""",

    "RBAC bypass when accessing admin endpoints via URL manipulation": """## Summary
Non-admin users can access admin-only API endpoints by directly navigating to admin URLs without proper role verification on the backend.

## Business Impact
Critical security vulnerability. Any authenticated user can perform admin actions including user management and configuration changes.

## Observed Behaviour
A SUPPORT_L1 user can call `DELETE /api/admin/users/42` successfully despite not having the ADMIN role.

## Expected Behaviour
All admin endpoints must verify the requesting user has the ADMIN role before processing the request.

## Reproduction Steps
1. Log in as a SUPPORT_L1 user
2. Send a request to any `/api/admin/*` endpoint
3. Observe that the request is processed without role verification

## Additional Notes
The admin router is missing the `Depends(require_admin)` dependency. All other protected routers have this guard.""",

    "Gunicorn worker timeout under sustained 200 req/s load": """## Summary
Gunicorn workers timeout and restart when the API receives sustained traffic above 200 requests per second for more than 5 minutes.

## Business Impact
Service degradation during high-traffic periods. Approximately 5% of requests fail with 503 during worker restarts.

## Observed Behaviour
Worker processes are killed with SIGKILL after exceeding the 30-second timeout. New workers spawn but take 5 seconds to initialize.

## Expected Behaviour
Workers should handle sustained load gracefully without timeouts.

## Reproduction Steps
1. Use `hey -z 10m -c 50 -q 200` to generate sustained load
2. Monitor Gunicorn worker lifecycle logs
3. Observe worker timeout and restart cycle

## Additional Notes
Consider switching from sync to async workers (uvicorn) or increasing worker count. Current: 4 workers, 30s timeout.""",
}


def generate_description(title: str, category: str) -> str:
    """Return a structured description for the given ticket title.

    If a hand-crafted description exists, use it. Otherwise, generate
    a structured template from the title and category.
    """
    if title in TICKET_DESCRIPTIONS:
        return TICKET_DESCRIPTIONS[title]

    # Fallback: generate a structured description from title/category
    return f"""## Summary
{title}

## Business Impact
This issue is affecting engineering productivity in the {category} domain. Multiple team members have reported encountering this problem during regular operations.

## Observed Behaviour
The system exhibits unexpected behavior as described in the title. The issue is reproducible across multiple environments.

## Expected Behaviour
The system should operate normally without the described issue. All {category.lower()} operations should complete within expected parameters.

## Reproduction Steps
1. Navigate to the affected {category.lower()} component
2. Perform the standard workflow that triggers this issue
3. Observe the unexpected behavior

## Additional Notes
This issue was first reported by the engineering team and has been confirmed in both staging and production environments."""
