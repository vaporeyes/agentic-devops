# Phase 0: Preflight

**Goal:** Prove the target cluster and repository match the declared starting
state. Change nothing on the cluster.

**Inputs:**

- A reachable Kubernetes cluster: kind (`local`) or EKS (`eks`)
- A dedicated kubeconfig file (never the ambient `~/.kube/config`)
- This repository at a committed revision

**Outputs:**

- A passing Phase 0 gate
- `evidence/phase-0.yaml` recording revision, context, server version, and
  the inventory hash

**Test criteria (`tests/phase_0/test_preflight.py`):**

- At least one node reports `Ready=True`
- Server version is at or above `metadata.kubernetes_min_minor`
- The `argocd` namespace does not exist
- No Argo CD Applications exist
- `components.yaml` validates: every component pinned and profile-scoped
- The repository is at a committed revision with a clean working tree

Static prerequisites (`tests/static/`) must also pass: inventory validator
rules, harness permissions, and audit hook behavior.

**Key decisions:**

- Install nothing. A failed read triggers investigation, not installation.
- If `argocd` already exists, do not delete it. Identify the owner and
  decide whether the cluster is reusable.
- Phase gates refuse to run without `KUBECONFIG_FILE` and
  `EXPECTED_CONTEXT`; a skipped gate is not a pass.

**Profile notes:**

- `local`: requires kind v0.33.0. Create the cluster from the pinned
  definition with a dedicated kubeconfig:
  `kind create cluster --config platform/profiles/local/kind-config.yaml
  --kubeconfig ~/.kube/agentic.kubeconfig`, then set
  `EXPECTED_CONTEXT=kind-agentic`. Never rely on kind's default node image;
  it changes with each kind release (v0.29.0 defaulted to 1.33, below the
  floor).
- `eks`: use a lab-specific kubeconfig and a context substring that names the
  lab cluster.

**Run:**

```bash
KUBECONFIG_FILE=~/.kube/agentic.kubeconfig EXPECTED_CONTEXT=kind-agentic \
  uv run --group test pytest tests/static tests/phase_0 -q
KUBECONFIG_FILE=~/.kube/agentic.kubeconfig \
  uv run --group test python scripts/record_evidence.py --phase 0 --gate-result passed
```

**Completion promise:** `<promise>PHASE0_DONE</promise>`

**Stop here.** Wait for approval before Phase 1.
