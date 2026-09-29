# Platform Build Specification

The contract the builder agent executes. Rationale lives in
[docs/book-analysis.md](../docs/book-analysis.md) and
[docs/framework-proposal.md](../docs/framework-proposal.md).

## End-to-End Outcome

A developer requests a governed agent service; the request produces
version-controlled artifacts; Argo CD reconciles them; admission policy
evaluates them; the workload reaches models and tools only through the
governed gateway; and the first trace arrives with no hand-edited cluster
state.

## Profiles

- `local`: kind on the development host. Fast iteration and CI.
- `eks`: the reference deployment. EBS gp3 storage, AWS Load Balancer
  Controller, EKS Pod Identity.

The platform is built to the production profile from day one. Security
posture is identical in every profile: SSO, persistent unsealed secrets,
durable state, digest-pinned signed images, authenticated and encrypted
traffic. Profiles differ only in which infrastructure provides a
capability (for example S3 on `eks`, an in-cluster object store on
`local`). There are no lab shortcuts in any profile; a static test fails
the build if one appears.

A component's `profiles` field in `components.yaml` decides where it is
deployed. Profile differences live in `platform/profiles/<profile>/`
overlays, never in forked manifests.

## Non-negotiable Rules

1. One phase at a time. Each phase ends with a stop; the next phase starts
   only on explicit human approval.
2. Test first. Run the phase gate, confirm it fails for the expected reason,
   build, confirm it passes. No mocks or stubs in phase gates.
3. The only direct cluster installs are the Argo CD bootstrap (Phase 1) and
   scripted server-side dry-run proofs. Everything else flows through Git.
   Use `kubectl apply --server-side --force-conflicts` for the bootstrap.
4. Pin every version from `components.yaml`. Validate values against the
   pinned chart (`helm show values`) and manifests against installed CRDs
   (server-side dry run); unknown keys and fields are silently dropped.
5. Two model roles: the builder (Claude Code) and the in-platform model
   served behind the gateway. They never share identity or credentials.
6. No secret values in Git, logs, test output, evidence, or model context.
7. All Kyverno policies ship with `failureAction: Audit`. Promotion to
   Enforce happens only in Phase 8, through Git, with paired fixtures.
8. Every control is proven with a paired test: the bad input is denied for
   the named reason, the good input still works.
9. Eventually consistent state is polled with a deadline; fixed sleeps are
   not allowed in tests.

## Known Failure Rules

Carry these into every manifest (all observed in the book's live build):

- Per-cluster values are parameters, never hardcodes; no `REPLACE_` tokens
  reach the cluster.
- `runAsNonRoot: true` always pairs with a numeric `runAsUser`.
- An image `repository` never repeats the registry host.
- The runtime UID must be able to traverse its working directory.
- Shared credentials come from exactly one Secret.
- Ignore controller-defaulted drift only for proven paths; use
  `jqPathExpressions` for arrays.
- Test the user-facing surface and current-generation conditions, not pod
  readiness.

## Phase Completion

A phase is complete when:

1. Its gate in `tests/phase_<n>/` passes against a declared cluster.
2. `tests/static/` passes.
3. The diff is reviewed and contains nothing outside the phase scope.
4. The phase is committed and tagged `checkpoint/phase-<n>`.
5. `scripts/record_evidence.py --phase <n> --gate-result passed` has written
   `evidence/phase-<n>.yaml`, which is committed.
6. The completion promise is printed, and the builder stops.

## Phases

| Phase | File                                                        | Outcome                                           |
| ----- | ----------------------------------------------------------- | ------------------------------------------------- |
| 0     | [phase-0-preflight.md](phases/phase-0-preflight.md)         | Verified start state; harness and inventory valid |
| 1     | [phase-1-foundation.md](phases/phase-1-foundation.md)       | Argo CD owns the foundation from Git              |
| 2     | [phase-2-observability.md](phases/phase-2-observability.md) | Metrics, logs, and traces proven end to end       |
| 3     | [phase-3-portal.md](phases/phase-3-portal.md)               | Backstage shows catalog and live Argo CD state    |
| 4     | [phase-4-gateway.md](phases/phase-4-gateway.md)             | Programmed AI gateway with mTLS and access logs   |
| 5     | [phase-5-model-serving.md](phases/phase-5-model-serving.md) | Model served and reachable only via the gateway   |
| 6     | [phase-6-agent-runtime.md](phases/phase-6-agent-runtime.md) | Guarded, traced agent with narrow MCP tools       |
| 7     | [phase-7-golden-path.md](phases/phase-7-golden-path.md)     | Form to running agent to trace, correlated        |
| 8     | [phase-8-governance.md](phases/phase-8-governance.md)       | One policy enforced; actions attributed           |
