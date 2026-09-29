# Phase 3: Developer Portal and Delivery Extensions

**Goal:** Backstage is the front door: real catalog entities with resolvable
owners and live Argo CD state through a backend proxy. Delivery extension
APIs are established.

**Inputs:** Phase 2 passed.

**Outputs:**

- A Backstage image we build, scan, and pin by digest (plugins: catalog,
  scaffolder, Argo CD, publisher for the org Git provider); TechDocs
  built externally in CI
- Backstage Application at the last foundation wave with
  `--config app-config.production.yaml`
- A single `backstage-integrations` Secret sourced through ESO; dedicated
  project-scoped Argo CD account and a Git provider App or machine user
  scoped to the agents organization or group (not admin credentials)
- Catalog: a Group entity and the platform Component with a resolvable owner
- Argo Workflows, Argo Events (with a JetStream EventBus), Argo Rollouts,
  and KEDA Applications

**Test criteria (`tests/phase_3/`):**

- Portal and extension Applications Synced and Healthy
- `scaledobjects.keda.sh`, `workflows.argoproj.io`, `sensors.argoproj.io`,
  and `rollouts.argoproj.io` report Established
- Catalog API returns at least one Component whose owner resolves to a Group
  (polled with deadline)
- Argo CD proxy returns live Applications
- Container args include the production config file

**Key decisions:**

- Backstage never deploys directly; it writes Git.
- Portal authentication is OIDC SSO with group resolution in every
  profile. Guest auth and `dangerouslyDisableDefaultAuthPolicy` are
  forbidden; catalog tests authenticate as a service principal.
- Backstage state lives in PostgreSQL (managed on `eks`), with a tested
  backup restore.

**Completion promise:** `<promise>PHASE3_DONE</promise>`

**Stop here.**
