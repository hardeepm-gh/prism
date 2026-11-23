# PRISM - GLPI Wiring (Verified Live)

GLPI: http://localhost:8081/ (forward on a fresh port, e.g. 18102:80), login glpi / glpi
App-Token (client prism-correlator-v4, Active, IPv4 0.0.0.0-255.255.255.255):
cjhEEDwNB3kPJWSiE0R9EfO3u9uMCYukKcFcbZmW
Secret: glpi-api in namespace aiops-m5

## Role
Correlator creates a GLPI ticket per root incident, Remediator closes it on execution:
Alertmanager webhook -> Correlator correlates -> GLPI ticket -> Approval -> Remediator -> Ticket closed/solved

## Verified tickets
- #1 Manual - baseline
- #2 Demo webhook (4-alert demo chain) - Solved, solvedate 2026-11-22
- #3 Real PrismRemediatorDown firing - auto-created
- #5 Real DemoAppSlow firing (30x /slow) - auto-created
- #6 DemoAppSlow re-fire - second ticket for same alert
- #7 Real DemoAppErrors firing (30x /fail) - auto-created, severity critical, path /fail

## Correlator endpoints (verified)
- GET /root-incidents -> latest root incident, e.g. parent DemoAppErrors, instance demo-app:8096,
  job prism-demo-app, path /fail, severity critical, glpi_ticket_id 7
- POST /webhook -> 200 OK when Alertmanager delivers
- Correlator log shows GLPI initSession status 200 when it opens a GLPI session

## Gotchas
- Do NOT use the raw GLPI REST API with a hand-built Session-Token from the secret -
  it fails with ERROR_SESSION_TOKEN_MISSING. Use the browser UI (http://localhost:18102/ -> Tickets)
  to verify tickets, or let the Correlator own the API session.
- Cockpit /api/live can be stale (Firing: [], Ticket: None) even when Correlator already created the ticket.
  Trust GET /root-incidents on the Correlator directly.
- Re-fires create new tickets. DemoAppSlow produced both #5 and #6. That is expected -
  the Correlator does not deduplicate a re-fire after resolve.
- If no ticket appears, check in order: (1) Is the Prometheus rule firing (not just pending)?
  (2) Did Correlator log POST /webhook 200? (3) Does /root-incidents show the incident? Only then check GLPI.

## End-to-end test (repeatable)
1. Forward demo-app on a fresh unused port, verify curl localhost:PORT/metrics | grep demo_http shows demo metrics.
2. 30x curl localhost:PORT/slow -> DemoAppSlow firing -> new GLPI ticket.
3. Wait ~2 min quiet -> DemoAppSlow inactive.
4. 30x curl localhost:PORT/fail -> DemoAppErrors pending -> firing -> new GLPI ticket.
5. Wait ~2 min quiet -> DemoAppErrors inactive.
