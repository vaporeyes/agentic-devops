# Phase 2: Observability Plane

**Goal:** Metrics, logs, and traces each have a producer, a store, and a
query path proven by a round trip.

**Inputs:** Phase 1 passed; cert-manager Healthy; default StorageClass.

**Outputs:**

- Applications for kube-prometheus-stack, Loki, Tempo, OTel Collector
  (daemonset, `service.enabled: true`), and OTel Operator
- Grafana data sources for Loki and Tempo with stable UIDs
- A log collection path into Loki (closes a book gap: the reference build
  had no log producer beyond the audit stream)
- A Collector processor promoting `X-Request-ID` to the `request.id` span
  attribute (closes a book gap needed by Phase 7 correlation)
- [docs/telemetry-contract.yaml](../../docs/telemetry-contract.yaml)
  enforced by a rendered-config test

**Test criteria (`tests/phase_2/`):**

- Observability Applications Synced and Healthy
- Prometheus and Alertmanager PVCs Bound
- Collector desired equals Ready on every node
- Grafana API lists Loki and Tempo data sources
- A fresh OTLP span (current timestamp) is searchable in Tempo within a
  bounded poll
- A fresh log line with a unique marker is queryable in Loki
- The rendered Collector trace pipeline is read and asserted, including
  processor order after presets

**Key decisions:**

- Tempo stays at 2.9.0 until the round-trip test passes on a newer line.
- `eks` disables scheduler, controller-manager, and etcd scrapes.
- No high-cardinality values as metric or Loki labels.

**Completion promise:** `<promise>PHASE2_DONE</promise>`

**Stop here.**
