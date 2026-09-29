# ABOUTME: Writes evidence/phase-N.yaml binding a passed phase gate to Git, cluster, and inventory.
# ABOUTME: Refuses dirty trees, failed gates, and payload fields; stores identifiers only.
"""Record phase-gate evidence.

Usage:
    KUBECONFIG_FILE=... uv run --group test python scripts/record_evidence.py \
        --phase 0 --gate-result passed [--extra trace_id=...]
"""

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_EXTRA = frozenset({"prompt", "response", "completion", "password", "token", "secret"})


def build_record(
    *,
    phase: int,
    git_revision: str,
    git_dirty: bool,
    kube_context: str,
    server_version: str,
    components_sha256: str,
    gate_result: str,
    extra: dict[str, str],
) -> dict[str, Any]:
    """Build an evidence record, rejecting states that cannot serve as evidence."""
    if git_dirty:
        raise ValueError("working tree is dirty; evidence must bind to a committed revision")
    if gate_result != "passed":
        raise ValueError(f"gate result is {gate_result!r}; only a passed gate is recorded")
    forbidden = sorted(key for key in extra if key.lower() in FORBIDDEN_EXTRA)
    if forbidden:
        raise ValueError(f"payload-like fields are not evidence: {forbidden} (e.g. prompt)")
    return {
        "phase": phase,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "git_revision": git_revision,
        "kube_context": kube_context,
        "server_version": server_version,
        "components_sha256": components_sha256,
        "gate_result": gate_result,
        **extra,
    }


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _kubectl(*args: str) -> str:
    kubeconfig = os.environ["KUBECONFIG_FILE"]
    return subprocess.run(
        ["kubectl", "--kubeconfig", kubeconfig, *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--gate-result", required=True)
    parser.add_argument("--extra", action="append", default=[], metavar="KEY=VALUE")
    args = parser.parse_args()

    extra = dict(item.split("=", 1) for item in args.extra)
    server = json.loads(_kubectl("version", "-o", "json"))["serverVersion"]["gitVersion"]
    record = build_record(
        phase=args.phase,
        git_revision=_git("rev-parse", "HEAD"),
        git_dirty=bool(_git("status", "--porcelain")),
        kube_context=_kubectl("config", "current-context"),
        server_version=server,
        components_sha256=hashlib.sha256((REPO_ROOT / "components.yaml").read_bytes()).hexdigest(),
        gate_result=args.gate_result,
        extra=extra,
    )
    out = REPO_ROOT / "evidence" / f"phase-{args.phase}.yaml"
    out.parent.mkdir(exist_ok=True)
    out.write_text(yaml.safe_dump(record, sort_keys=False))
    print(f"wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
