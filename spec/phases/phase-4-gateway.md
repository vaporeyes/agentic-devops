# Phase 4: Governed AI Gateway

**Goal:** A programmed agentgateway data path with ownership separation,
client-certificate mTLS, access logging, and AI policies in Audit.

**Inputs:** Phase 3 passed.

**Outputs:**

- Waves: 0 Gateway API CRDs v1.5.1 (vendored); 1 kgateway and agentgateway
  CRDs; 2 controllers; 3 runtime Gateways, backends, routes, policies
- `agentgateway-proxy` Gateway (closes a book gap: the reference repo
  installed the controller but no Gateway). On `eks`, annotate the generated
  LoadBalancer internal via `spec.infrastructure.annotations`.
- `agentgateway-mtls` Gateway using `spec.tls.frontend` client validation
- An AgentgatewayPolicy configuring `spec.frontend.accessLog` with the
  audit event fields from
  [docs/telemetry-contract.yaml](../../docs/telemetry-contract.yaml)
- Listener `allowedRoutes` via namespace selector
  `agentic-platform.io/attach-agentgateway: "true"`
- Default-deny NetworkPolicy for AI namespaces with explicit gateway flows
- Kyverno AI policies in Audit: guardrail reference on Agents, registry
  allowlist (organization path, not a registry wildcard), OTel annotation,
  direct-provider bypass detection

**Test criteria (`tests/phase_4/`):**

- GatewayClass Accepted; both Gateways `Programmed=True`
- A probe route reports `Accepted=True` and `ResolvedRefs=True`
- mTLS paired proof: without client cert fails, with trusted cert succeeds
  (both requests reach a route; a 404 is not a pass)
- A request produces an access-log record that passes the audit-shape
  validator
- One fixture per AI policy produces a PolicyReport failure
- Static: agentgateway values contain only keys present in
  `helm show values` for v1.3.0

**Completion promise:** `<promise>PHASE4_DONE</promise>`

**Stop here.**
