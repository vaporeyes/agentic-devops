# Trust Boundaries

One misuse case and at least one control outside the model per boundary.
A boundary whose only protection is an instruction is incomplete.

## Builder to Cluster

- Identity: `claude-code-builder-<env>` with a dedicated kubeconfig
- Misuse case: mutation against the wrong context, or a live patch
- Reasoning control: phase spec and GitOps-only rule
- Infrastructure control: ask rules on mutations, context guard in tests,
  RBAC on the builder credential
- Evidence: audit hook JSONL; Argo CD drift status

## Developer to Portal to Git

- Identity: SSO user (lab: guest, `local` only)
- Misuse case: template input supplies an arbitrary model URL or tool
- Reasoning control: enums from the capability registry
- Infrastructure control: AppProject kind and namespace whitelist; Kyverno
- Evidence: scaffolder task log, Git commit, catalog entity

## Git to Argo CD to Kubernetes API

- Identity: Argo CD application controller
- Misuse case: generated repo deploys cluster-scoped or foreign-namespace
  resources
- Infrastructure control: AppProject destinations and whitelist; admission
- Evidence: Application sync revision; PolicyReport

## Runtime Agent to Gateway to MCP Tool

- Identity: agent service account
- Data crossing: tool name, structured arguments, structured result
- Misuse case: model requests an unapproved write operation
- Reasoning control: tool descriptions expose read operations only
- Infrastructure control: tool allowlist in Agent spec; gateway MCP
  authorization; tool server rejects writes for this identity
- Evidence: gateway access log and OpenTelemetry span
- Failure response: deny, report the reason, preserve the trace

## Runtime Agent to Gateway to Model

- Misuse case: prompt injection, or direct call bypassing the gateway
- Infrastructure control: guardrail webhook (fail closed); NetworkPolicy on
  the predictor; no provider credentials in agent namespaces
- Evidence: guardrail decision in access log; span with model attributes

## Workload to Secret Provider

- Misuse case: one team references another team's secret path
- Infrastructure control: store scope, OpenBao policy per path, RBAC
- Evidence: ESO conditions; OpenBao audit device (production)

## Telemetry Producer to Collector

- Misuse case: prompts or credentials exported into traces and logs
- Infrastructure control: redaction processor; sensitive-field list in the
  telemetry contract; canary-secret test
- Evidence: canary absent from Loki and Tempo
