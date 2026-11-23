# PRISM - Prometheus Wiring (Verified Live)

Cluster: Kind aiops-m5, namespace aiops-m5
Prometheus: Deployment prometheus, ConfigMap prometheus-config, Rules ConfigMap prometheus-rules
Port (use a fresh alternate port each time): kubectl -n aiops-m5 port-forward svc/prometheus 19099:9090

## What Prometheus does in PRISM
- Scrapes 6 targets every 15s (scrape_interval: 15s)
- Evaluates 6 rules in group prism
- Sends firing alerts to Alertmanager at alertmanager:9093

## Config - prometheus.yml
- global: scrape_interval 15s
- rule_files: /etc/prometheus/rules/prism.yml
- alerting: alertmanagers -> alertmanager:9093
- scrape_configs: prometheus (localhost:9090), prism-correlator (correlator:8089),
  prism-remediator (remediator:8090), prism-approval-gateway (approval-gateway:8087),
  prism-demo-app (demo-app:8096), prism-cockpit (cockpit:8095)

## Rules - prism.yml
- PrismCorrelatorDown: up{job="prism-correlator"} == 0, for 30s, critical
- PrismRemediatorDown: up{job="prism-remediator"} == 0, for 30s, critical
- PrismApprovalGatewayDown: up{job="prism-approval-gateway"} == 0, for 30s, critical
- PrismCockpitDown: up{job="prism-cockpit"} == 0, for 30s, warning
- DemoAppSlow: histogram_quantile(0.95, rate(demo_http_duration_seconds_bucket[2m])) > 1, for 30s, warning
- DemoAppErrors: rate(demo_http_errors_total[2m]) > 0.05, for 30s, critical

## Key gotchas (hit live)
1. rate() needs a range vector: rate(metric[2m]), NOT rate(metric).
   Missing range crashes Prometheus with: expected type range vector in call to function "rate", got instant vector.
2. When copy/paste strips the range, rebuild the file with chr(91)/chr(93) in Python instead of typing it literally.
3. Never trust a port-forward blindly. Stale forwards on 18096/18097 served Cockpit/Correlator HTML, not demo-app.
   Always verify: curl localhost:PORT/metrics | grep demo_http
4. After a restart, wait for Ready before forwarding:
   kubectl -n aiops-m5 wait --for=condition=ready pod -l app=prometheus
5. If Endpoints is empty, the Service has no healthy pod - fix the pod first, not the forward.

## Verification (verified live)
- curl localhost:19099/-/healthy -> Prometheus Server is Healthy.
- /api/v1/targets?state=active -> 6 targets, all health=up
- /api/v1/rules -> 6 rules, all inactive when quiet
- After 30x /slow: DemoAppSlow firing
- After 30x /fail: DemoAppErrors pending -> firing
- After traffic stops (~2 min): both back to inactive

## Demo-app metrics (must exist for the rules to work)
services/demo-app/app/main.py defines:
- demo_http_requests_total{path,status} - Counter
- demo_http_errors_total{path} - Counter
- demo_http_duration_seconds{path} - Histogram
If /metrics shows only python_* / prism_* and no demo_http_*, the forward is pointing at the wrong service.
Check inside the pod: kubectl -n aiops-m5 exec deployment/demo-app -- cat /app/app/main.py
