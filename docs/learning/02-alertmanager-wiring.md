# PRISM - Alertmanager Wiring (Verified Live)

## Role
Prometheus (firing alert) -> Alertmanager :9093 -> Correlator POST /webhook -> GLPI ticket

## Config essentials
- Prometheus alerting.alertmanagers -> alertmanager:9093
- Alertmanager receiver -> Correlator webhook: http://correlator:8089/webhook
- Verify Prometheus sees Alertmanager: activeAlertmanagers shows alertmanager:9093

## Verification (verified live)
- Forward on a fresh port: kubectl -n aiops-m5 port-forward svc/alertmanager 19100:9093
- Correlator log shows: POST /webhook 200 OK after each firing alert
- Alertmanager /api/v2/alerts may print empty depending on grouping/filter - do not rely on it alone.
  The Correlator POST /webhook log line is the proof of delivery.

## Alert lifecycle
- inactive -> pending (condition true, for: 30s not yet met) -> firing (sent to Alertmanager) -> inactive
- Alertmanager only forwards firing, not pending. If Correlator shows nothing, check whether the rule is still pending.
- After traffic stops, alerts resolve on their own in ~1-2 min. No manual clear needed.

## Gotchas
- A stale port-forward can make it look like Alertmanager/Correlator received nothing. Always verify the forward.
- If Prometheus is crashing, Alertmanager gets nothing - fix Prometheus first.
