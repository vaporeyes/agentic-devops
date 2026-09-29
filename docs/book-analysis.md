# Book Analysis: Agentic DevOps with Claude Code

Source: Michael Forrester, *Agentic DevOps with Claude Code* (Packt, ISBN
9781808344190). Companion repository:
<https://github.com/PacktPublishing/Agentic-DevOps-with-Claude-Code>.

## Thesis

AI capabilities (agents, model endpoints, MCP tools, guardrails) are a new
*workload type* on an existing cloud-native platform, not a parallel,
ungoverned lane. They inherit the same Git source of truth, reconciliation,
identity, secrets, admission policy, and telemetry as everything else. The
book demonstrates this through a live build of a 30-component (33-capability)
internal developer platform on EKS, assembled by Claude Code under a governed
build loop.

The recurring slogan is "read-only first, always": trust how an agent
observes before letting it change anything.

## Durable Principles

These survive any product swap and are the real payload of the book.

1. **Outcomes over components.** Define done as testable operational
   statements before choosing tools. A Running pod is never evidence.
2. **Git is authoritative.** One narrow bootstrap exception (Argo CD plus
   root Application), then every change flows through Git. Repair faults at
   the source, never with live patches.
3. **Separate identities by role.** The builder agent (Claude Code), the
   runtime agent, and the served model get distinct identities, permissions,
   lifecycles, and evidence. No permission inheritance by convenience.
4. **Two control layers.** Reasoning-layer controls (specs, prompts,
   allow/ask/deny rules) shape behavior; infrastructure controls (RBAC,
   admission, NetworkPolicy, gateways, workload identity) bound it. Every trust
   boundary needs at least one control outside the model.
5. **Mediated traffic.** All model, MCP, and agent-to-agent traffic crosses one
   governed gateway that authenticates, authorizes, guards, and logs.
6. **Policy lifecycle is audit, measure, remediate, enforce.** Promotion is a
   Git release with fixtures, monitoring, and rollback.
7. **Paired proofs.** Every control is shown to deny the bad input for the
   intended reason and admit the good input.
8. **Evidence and correlation.** Actor, agent, request ID, Git revision, and
   trace ID join every hop. Metadata-first logging; no raw prompts by default.
9. **Pin behavior, not versions.** A pin preserves verified behavior (the
   Tempo 2.10 regression). "Latest" is not a control; the acceptance test is.
10. **Defects become contracts.** Every live failure leaves behind a test,
    health rule, or runbook.

## Architecture

Three planes, stacked as a dependency and ownership model (not separate
clusters). GitOps, policy, and observability cut across all three.

| Plane        | Owns                                                         | Proves                                            |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------- |
| Foundation   | GitOps, certs, secrets, storage, identity, policy, telemetry | Desired state reconciles; secrets and traces flow |
| AI           | Gateways, agents, MCP tools, guardrails, model serving       | Agent reconciles; guarded request completes       |
| Self-service | Backstage templates, ApplicationSet discovery                | Form submission becomes a running, traced service |

### Component Inventory (as pinned in the book)

| Area            | Component                              | Version / notes                                 |
| --------------- | -------------------------------------- | ----------------------------------------------- |
| GitOps          | Argo CD                                | chart 9.5.22, app v3.4.4, server-side apply     |
| Git source      | Gitea (in-cluster)                     | Workshop distribution machinery                 |
| Certificates    | cert-manager                           | v1.20.2, sync wave 0                            |
| Secrets         | OpenBao + External Secrets Operator    | OpenBao dev mode (lab only); ESO API v1         |
| Policy          | Kyverno                                | 1.18.1, ClusterPolicy, per-rule failureAction   |
| Storage         | EBS CSI + gp3 StorageClass             | Single default, encrypted, WaitForFirstConsumer |
| Cloud identity  | EKS Pod Identity                       | IRSA disabled                                   |
| Ingress         | AWS Load Balancer Controller           | No MetalLB, no ingress-nginx (EOL March 2026)   |
| Metrics         | kube-prometheus-stack                  | chart 86.3.2, Prometheus v3.12, Grafana v13.0.2 |
| Logs            | Loki                                   | SingleBinary, filesystem (lab only)             |
| Traces          | Tempo                                  | 2.9.0 / chart 1.25.0 (2.10 search regression)   |
| Collection      | OTel Collector (daemonset) + Operator  | eks detector removed                            |
| Portal          | Backstage (custom image)               | 1.51 line, chart 2.8.2, in-memory SQLite (lab)  |
| Delivery        | Argo Workflows, Events, Rollouts; KEDA | Workflows v4.0; Events needs JetStream EventBus |
| Gateway API     | Upstream CRDs                          | v1.5.1                                          |
| Gateways        | kgateway / agentgateway                | v2.3.4 / v1.3.0, sibling controllers            |
| Agents          | kagent + KMCP                          | v0.9.9, Agent API kagent.dev/v1alpha2           |
| Guardrails      | LLM Guard API                          | 0.3.16, dormant project, needs webhook adapter  |
| Model serving   | KServe + vLLM CPU (Qwen3-1.7B)         | KServe 0.19.0, vLLM 0.23.0, RawDeployment       |
| GenAI telemetry | OpenLLMetry (traceloop-sdk)            | 0.61.0 pinned with openai 1.109.1               |
| Distributed     | llm-d                                  | v0.7.0, architecture reference only             |

## Operating Model for the Builder Agent

- **Phase 0 preflight:** no-change gate proving nodes Ready, pinned K8s line,
  no existing Argo CD, and a valid `components.yaml`.
- **Phase contracts:** each phase file states Goal, Inputs, Outputs, Test
  criteria, Key decisions (not re-litigated), Completion promise, and Stop.
- **Control loop:** observe, prove red, build through Git, validate live
  outcome, review diff, commit and tag checkpoint, print promise, stop for a
  human.
- **Harness:** tracked `defaultMode` that prompts (never `bypassPermissions`),
  allow for reads, ask for mutations, deny for secrets and `.claude/**`, plus
  PreToolUse/PostToolUse JSONL audit hooks with a named `agent_identity`.
- **Test harness:** `conftest.py` binds kubectl to `KUBECONFIG_FILE` and
  aborts if `EXPECTED_CONTEXT` does not match. Unset variables skip tests and
  exit green, so skip counts must be read.

## Phase Map

| Phase | Chapter | Outcome gate                                                            |
| ----- | ------- | ----------------------------------------------------------------------- |
| 0     | 2       | Preflight: cluster reachable, bare, inventory pinned                    |
| 1     | 3       | Argo CD owns foundation; ExternalSecret materializes; one default SC    |
| 2     | 4       | PVCs Bound, Collector on every node, Grafana sources, trace round-trip  |
| 3     | 5       | Catalog returns entities; Argo CD proxy returns live Applications       |
| 4     | 6       | Gateway Programmed; route Accepted and ResolvedRefs; mTLS paired proof  |
| 5     | 7       | Agent Ready for current generation; MCP bound; injection blocked        |
| 6     | 8       | PredictorReady; runtime contract asserted; inference and tool-choice ok |
| 7+    | 9       | Form to repo to Application to Agent to route to trace, correlated      |
| Final | 10      | One policy enforced with deny/admit fixtures; attributed Loki events    |

## Gaps in the Reference Repository

The book is candid that the maintained repository stops short in several
places. Any framework built from it must close these explicitly.

| Gap                                                     | Where    | Impact                                           |
| ------------------------------------------------------- | -------- | ------------------------------------------------ |
| No runtime agentgateway Gateway object                  | Ch 6     | Controller installed but no data path            |
| No MCP backend, route, RemoteMCPServer, or tool binding | Ch 6, 7  | Mediated MCP described, not implemented          |
| LLM Guard webhook adapter not shipped                   | Ch 7     | Policy points at a missing Service; fails closed |
| Demo ModelConfig points directly at KServe              | Ch 7     | Bypasses gateway guardrail and audit             |
| No `/agents` route; Service port is 8080, not 80        | Ch 7, 9  | Golden-path invocation returns 503/404           |
| Agent speaks A2A JSON-RPC, not OpenAI chat schema       | Ch 9     | Invocation body must come from the agent card    |
| Gateway access log policy not configured                | Ch 6, 8  | No gateway audit records                         |
| No log collection pipeline (filelog or agent)           | Ch 4, 10 | Loki has only the Claude audit stream            |
| `X-Request-ID` not promoted to `request.id` span attr   | Ch 9     | Correlation query silently returns nothing       |
| TechDocs toolchain absent from Backstage image          | Ch 5     | Docs never build; prefer external builder in CI  |
| Rollouts Gateway API plugin not installed               | Ch 5     | Progressive traffic shifting is design only      |
| KServe top-level Ready is False in internal topology    | Ch 8     | Needs PredictorReady-based health customization  |
| Agentgateway always creates a public LoadBalancer       | Ch 6     | Must annotate internal; unauthenticated listener |
| Browser terminal: unauthenticated, cluster-admin        | Ch 1, 10 | Production blocker                               |
| Kyverno ClusterPolicy deprecated (removal in 1.20)      | Ch 10    | New rules should use ValidatingPolicy            |

## Lab Shortcuts to Replace for Production

- Guest Backstage auth and `dangerouslyDisableDefaultAuthPolicy`.
- OpenBao dev mode with a fixed root token in Git.
- In-memory SQLite for Backstage; filesystem Loki; local Tempo storage.
- Admin-minted Argo CD token and Gitea admin password as portal credentials.
- `ghcr.io/*` registry allowlist (too broad); mutable tags instead of digests.
- Plaintext in-cluster traffic (Collector to Tempo, gateway listener).
- Small CPU model; no GPU capacity plan, quotas, or cost attribution.
- Single cluster; no canary rollout, orphan sweep, or DR rehearsal.

## Recurring Failure Classes (turn into contract tests)

- Controller-default drift: diff desired vs live, ignore only proven paths,
  use `jqPathExpressions` for arrays.
- Configuration not loaded: assert container args and a functional API.
- Placeholder escape: scan rendered output for a family of markers.
- Image/runtime mismatch: digest, platform, UID, flags, smoke response.
- Remote source failure: vendor bases, render offline.
- Eventual consistency: poll the exact condition with deadline and jitter.
- False health: test the user-facing surface and current-generation status.
- Silent config: Helm ignores unknown values; API server prunes unknown
  fields. Validate against the pinned chart schema and installed CRD.

## Assessment

Strengths: the operating discipline (phase contracts, paired proofs, evidence
records, audit-to-enforce) is excellent and tool-agnostic. The honesty about
defects and repository gaps is unusually useful for implementers.

Weaknesses for direct adoption: the stack is EKS-specific and large for a
first deployment; several AI-plane integrations are specified but not built;
many AI components are alpha or pre-1.0 (kagent v1alpha2, agentgateway
v1alpha1 policy CRDs, llm-d, GenAI semconv) and LLM Guard is dormant. Expect
to own the adapter, the MCP wiring, and the correlation plumbing.
