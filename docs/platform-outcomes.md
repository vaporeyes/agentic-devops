# Platform Outcomes

Every architectural decision must support these outcomes. Each outcome lists
the evidence that proves it; the phase gate named in brackets executes it.

## Developer Outcome

A developer can request a governed agent service without learning the
implementation details of platform components.

- A form with name, owner, purpose, model alias, and approved tools yields a
  running agent and its first trace [phase 7].

## Delivery Outcome

Every generated resource is stored in Git and reconciled by Argo CD.

- Every change after bootstrap traces to a Git revision [phases 1, 7].
- Deleting a generated agent from the cluster restores it from Git without
  a manual apply [phase 7].

## Runtime Outcome

Model and tool traffic uses approved gateways, identities, and policies.

- Every runtime agent has a named identity and bounded permissions
  [phase 6].
- Direct predictor or provider access from agent namespaces is refused
  [phase 5].
- A prompt-injection fixture is blocked while a benign control passes
  [phase 6].

## Operator Outcome

The platform exposes live health, policy results, logs, metrics, and traces.

- A fresh trace and log line round-trip through the pipeline [phase 2].
- A model or tool call produces a queryable span and access-log event
  [phases 4, 6].
- A denied request produces an understandable policy result [phase 8].

## Safety Outcome

No agent receives an unrestricted path to change the cluster or network.

- Agents bind only named read-only tools; write tools require approval and a
  separate identity [phase 6].
- Every agent and human action is attributable in Loki [phase 8].

## Recovery Outcome

A platform failure can be repaired at the source without an unrecorded
cluster patch.

- Each material defect leaves a regression test or runbook [all phases].
