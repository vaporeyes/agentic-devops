# Phase 7: Governed Self-Service Golden Path

**Goal:** A short Backstage form produces a governed agent service through
Git and Argo CD, verified as one correlated chain from form to trace.

**Inputs:** Phase 6 passed.

**Outputs:**

- `templates/agent-service/` (scaffolder v1beta3): inputs name, owner
  (OwnerPicker), purpose, model alias, approved tools; all else platform-owned
- Capability registry (model aliases, approved tools, data class) consumed
  by the template enums
- Skeleton: `catalog-info.yaml`, `agent-service.yaml` contract marker,
  `manifests/agent.yaml`, `manifests/httproute.yaml`, `README.md`,
  `tests/test_contract.py`
- AppProject `agent-services`: sources limited to the agents org,
  destination `kagent` only, whitelist Agent and HTTPRoute
- ApplicationSet (SCM provider generator for the org Git provider,
  `missingkey=error`, filter on the contract marker and `manifests`)
- Template-repo contract tests run in CI (placeholder scan lives outside
  the skeleton)

**Test criteria (`tests/phase_7/`):**

- Scaffolder action inventory contains `fetch:template`, the provider
  publish action (`publish:github` or `publish:gitlab`), and
  `catalog:register`
- Generated repo passes its contract tests
- Exactly one Application for the repo, synced to the repo head SHA
- Agent Ready for current generation; route Accepted and ResolvedRefs
- A safe invocation with a unique `X-Request-ID` returns and its trace is
  found by service name and `request.id`
- No non-passing PolicyReport results for the generated Agent
- Stage durations recorded against the initial objectives in the book

**Completion promise:** `<promise>PHASE7_DONE</promise>`

**Stop here.**
