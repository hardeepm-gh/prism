# Exp 7: Default-deny blocks all

Applied NetworkPolicy podSelector: {} + Ingress/Egress
Result: cockpit -> correlator-test curl times out BLOCKED

Also DNS blocked - need to allow kube-system DNS

Learning: default-deny is powerful but needs allow for DNS and explicit app flows
