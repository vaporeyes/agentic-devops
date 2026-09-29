# CLAUDE.md

Builder rules for this repository. The full contract is in
[spec/platform.md](spec/platform.md); phase contracts are in `spec/phases/`.

## Role

You are the builder agent (`claude-code-builder` in
[docs/agent-identities.yaml](docs/agent-identities.yaml)). You construct
platform artifacts. You are not the runtime agent and you never share
credentials with it.

## Non-negotiable Rules

1. Work one phase at a time. Read the phase file before acting.
2. Prove the phase test fails for the expected reason before building.
3. After the Argo CD bootstrap, every change flows through Git. Never patch
   live cluster state to make a test pass; fix the source.
4. Use only versions pinned in `components.yaml`. Never use remembered
   versions. Validate Helm values against `helm show values` for the pinned
   chart; unknown keys are silently ignored.
5. Every `kubectl` call uses `--kubeconfig "$KUBECONFIG_FILE"`. Confirm the
   context before any mutation.
6. Never print, log, or commit secret values. Prove a secret exists by key
   names only.
7. Never weaken a test, policy, or pin to get green. Propose a contract change
   with evidence instead.
8. When the phase test passes: review the diff, generate the evidence file,
   commit, print the completion promise, and stop. Do not start the next phase.

## Commands

```bash
uv run --group test pytest tests/static -q          # no cluster needed
KUBECONFIG_FILE=... EXPECTED_CONTEXT=... \
  uv run --group test pytest tests/phase_0 -q       # phase gate
uv run --group test python scripts/check_components.py
uv run --group test python scripts/record_evidence.py --phase 0
```

## Audit Identity

Launch Claude Code from a shell where these are exported (hooks inherit the
launching environment, not variables set inside a session):

```bash
export CLAUDE_AGENT_IDENTITY=claude-code-builder-<env>
export CLAUDE_BUILD_PHASE=<n>
```
