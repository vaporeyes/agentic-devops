# Phase 8: Enforcement, Attribution, Production Gaps

**Goal:** One narrow policy is enforced with paired proof and rollback;
agent and human actions are attributable; production gaps are owned.

**Inputs:** Phase 7 passed; audit results for the candidate policy have an
owner and disposition.

**Outputs:**

- Enforced rule for Agent metadata controls (owner, guardrail,
  template version), promoted through Git. New rules are written as
  ValidatingPolicy; existing ClusterPolicy rules use per-rule
  `failureAction`.
- Fixtures: one known-good and one per missing control
- Builder audit stream and gateway access logs shipped to Loki
- Production gap backlog with owners and dates (identity, terminal access,
  secrets, persistence, supply chain, model capacity, cost, retention,
  recovery, multi-cluster)

**Test criteria (`tests/phase_8/`):**

- Static: rendered rule `failureAction == Enforce`; no deprecated top-level
  `validationFailureAction`
- Offline `kyverno apply` against fixtures matches expectations
- Server-side dry run: each bad fixture denied naming the rule; good fixture
  admitted (a failure for any other reason is not a pass)
- Loki: exactly one attributed `mcp_tool_call` for a unique request ID with
  actor, agent, capability, outcome, and a 32-character trace ID
- Loki: zero parse errors and zero unattributed action events in the window
- Rollback rehearsal: reverting the commit returns the rule to Audit

**Completion promise:** `<promise>PHASE8_DONE</promise>`

**Stop here.**
