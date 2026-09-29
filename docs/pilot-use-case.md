# Pilot Use Case

The first bounded, read-only agent workflow. Status: accepted 2026-09-29.

## Selection Criteria

From the book's adoption guidance, a good pilot is:

- Painful and frequent enough to have a measurable manual baseline
- Read-only, with a benign failure mode (a bad answer is ignored, not
  executed)
- Served by data sources the platform already owns, so it adds no new data
  boundary
- Owned by a team that will be on call for it
- Evaluable against a fixed, repeatable case set

## Candidates

| Candidate                        | Data sources                     | New boundary   | Eval set           | Fit    |
| -------------------------------- | -------------------------------- | -------------- | ------------------ | ------ |
| GitOps-aware alert enrichment    | Alertmanager, K8s, Loki, Argo CD | None           | Induced faults     | Best   |
| Kubernetes event summarization   | K8s events                       | None           | Weak (no outcome)  | Subset |
| Change evidence gathering        | Git, Argo CD diff, PolicyReports | None           | Historical changes | Good   |
| Incident handoff preparation     | Alerts, traces, chat history     | Chat system    | Hard to score      | Later  |
| Network triage (BGP, interfaces) | Network devices, NMS             | Network estate | Needs lab devices  | Domain |

## Recommendation: GitOps-Aware Alert Enrichment

When a platform alert fires, the agent gathers read-only evidence and
returns a structured triage note: what is failing, current state, the Git
revision and Argo CD status behind it, relevant events and log excerpts,
hypotheses labeled as hypotheses, and the next safe check. The engineer
remains the decision maker.

### Why This One

- **No new data boundary.** Every source (Alertmanager, Kubernetes API,
  Loki, Prometheus, Argo CD) exists after Phases 1 to 3. Production posture
  from day one is easier when the pilot adds no external system.
- **The evaluation set already exists.** The book's live-build defects are
  reproducible faults that can be induced through Git on a non-production
  cluster: bad image tag (ImagePullBackOff), controller drift (OutOfSync),
  PVC Pending, ExternalSecret not materializing, missing webhook
  certificate, unresolved HTTPRoute, runAsNonRoot without numeric UID. Each
  has a known root cause to score against.
- **It exercises every platform control.** Trigger through Argo Events,
  mediated model and MCP traffic, guardrail, attribution, and traces all
  sit on the path.
- **The first customer is the platform team.** Owners and on-call already
  exist; there is no onboarding dependency on another team.
- **It generalizes.** Once proven, the same agent scoped by namespace serves
  application teams through the golden path.

### Flow

1. Alertmanager sends the alert to an Argo Events webhook EventSource.
2. A Sensor triggers a Workflow that invokes the agent over A2A through
   agentgateway, carrying `X-Request-ID` and the alert fingerprint.
3. The agent calls read-only MCP tools and the model through the gateway.
4. The agent returns a structured result (JSON schema, versioned).
5. The Workflow, not the agent, posts the note to the alert channel. The
   agent holds no write tool and no channel credential.

### Tools (purpose-built MCP server `platform-readonly`)

| Tool             | Inputs                                | Bounds                             |
| ---------------- | ------------------------------------- | ---------------------------------- |
| `get_pods`       | namespace, label selector             | Allowed namespaces; 50 pods max    |
| `get_events`     | namespace, involved object, since     | 30 minutes max window; 100 events  |
| `get_logs`       | namespace, pod, container, previous   | 200 lines; redaction applied       |
| `get_argocd_app` | application name                      | Sync, health, revision, conditions |
| `query_metric`   | named query from an allowlist, labels | No free-form PromQL                |

This server replaces the `everything` reference server in Phase 6, and its
tool names become the golden-path template enum in Phase 7.

### Evaluation and Stop Conditions

- Case set: 10 to 15 induced faults, each with a recorded root cause.
- Baseline: an engineer triages the same cases manually; record time to
  evidence and completeness.
- Scores per case: root cause among the top two hypotheses; evidence
  completeness; unsupported claims; tool errors; latency; cost.
- Targets to confirm: zero unsupported claims presented as fact, root cause
  in the top two for at least 80 percent of cases, time to evidence under
  the manual median.
- Stop immediately on: any attempted write, any secret in output or
  telemetry, any tool call outside the allowlist.

## Phase Impact

- Phase 3: Argo Events EventSource and Sensor for Alertmanager.
- Phase 6: build `platform-readonly` MCP server (we own it: tests, image,
  signing) and the result schema; `platform-helper` becomes the triage
  agent.
- Phase 7: template tool enum drawn from `platform-readonly`.
- Phase 8: attribution tests use triage requests.

## When to Choose Differently

- If the organization's pain is network operations, network triage is the
  higher-value pilot, but it adds a network-estate data boundary and needs
  lab devices for evaluation.
- If alert volume is dominated by application teams, keep this design but
  start with one volunteer team's namespaces in Phase 7.
