# Phase 1: GitOps Bootstrap and Foundation

**Goal:** Argo CD owns the foundation from Git after one audited bootstrap.
Certificates, secrets, storage, identity, and audit-mode policy converge.

**Inputs:** Phase 0 passed; the platform repository on the organization's
Git provider (GitHub or GitLab) with branch protection, reachable from the
cluster through a read-only deploy credential delivered by ESO.

**Outputs:**

- `bootstrap/argocd-values.yaml` and `bootstrap/root-app.yaml`
- `platform/1-foundation/<component>/application.yaml` with sync waves:
  0 cert-manager (and AWS LBC on `eks`), 1 issuers, OpenBao, ESO, Kyverno,
  2 configuration, 6 policy baseline
- Profile overlays: `local` uses the kind default StorageClass; `eks`
  creates the single default encrypted gp3 class and Pod Identity roles
- A ClusterSecretStore and a demo ExternalSecret
- Kyverno baseline policies in Audit
- `tests/static/test_rendered_manifests.py`: placeholder scan, image
  registry host not repeated, `runAsNonRoot` paired with numeric
  `runAsUser`, every `failureAction` is `Audit`

**Test criteria (`tests/phase_1/`):**

- Argo CD server, repo-server, and application-controller Ready
- Root Application and all foundation children Synced and Healthy
- Exactly one default StorageClass (gp3 on `eks`)
- ClusterSecretStore Ready and the demo ExternalSecret materializes its
  target Secret (asserted by key names only)
- No Application OutOfSync

**Key decisions:**

- The bootstrap is the only direct install: render the pinned chart,
  server-side dry run, then apply with `--server-side --force-conflicts`.
- The bootstrap values include the KServe health customization keyed on
  `PredictorReady` (used in Phase 5), tested against condition fixtures.
- OpenBao runs with persistent storage, a documented unseal mechanism
  (AWS KMS auto-unseal on `eks`; the `local` mechanism is decided and
  recorded in this phase), and Kubernetes auth. Dev mode and fixed root
  tokens are forbidden in every profile.
- Kyverno image verification (Audit): images from our ECR registry must
  carry a cosign signature from the platform AWS KMS key. The `local`
  profile pulls the same signed digests from ECR.
- `tests/static/test_no_lab_shortcuts.py` fails on: OpenBao dev mode,
  root tokens in Git, `dangerouslyDisableDefaultAuthPolicy`, guest auth,
  in-memory databases for stateful services, mutable image tags, and
  plaintext listeners without a recorded exception.

**Completion promise:** `<promise>PHASE1_DONE</promise>`

**Stop here.**
