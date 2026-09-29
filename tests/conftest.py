# ABOUTME: Shared pytest fixtures binding every cluster call to an explicit kubeconfig and context.
# ABOUTME: Phase gates refuse to run without a declared cluster, so a skipped gate never reads green.
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
KUBECONFIG_FILE = os.environ.get("KUBECONFIG_FILE", "")
EXPECTED_CONTEXT = os.environ.get("EXPECTED_CONTEXT", "")
PHASE_DIR_PREFIX = "phase_"


def _is_phase_gate(item: pytest.Item) -> bool:
    return any(part.startswith(PHASE_DIR_PREFIX) for part in Path(item.fspath).parts)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Abort before any test runs if a phase gate lacks an explicit, verified target."""
    if not any(_is_phase_gate(item) for item in items):
        return
    if not (KUBECONFIG_FILE and EXPECTED_CONTEXT):
        pytest.exit(
            "phase gates require KUBECONFIG_FILE and EXPECTED_CONTEXT; refusing to run "
            "(a skipped gate would report green without proving anything)",
            returncode=2,
        )
    context = current_context()
    if EXPECTED_CONTEXT not in context:
        pytest.exit(
            f"context {context!r} does not contain EXPECTED_CONTEXT {EXPECTED_CONTEXT!r}",
            returncode=2,
        )


def run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)


def current_context() -> str:
    result = run(["kubectl", "--kubeconfig", KUBECONFIG_FILE, "config", "current-context"])
    if result.returncode != 0:
        pytest.exit(f"cannot read kubeconfig {KUBECONFIG_FILE}: {result.stderr.strip()}", 2)
    return result.stdout.strip()


def kubectl(*args: str, check: bool = True, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run kubectl bound to the explicit kubeconfig."""
    result = run(["kubectl", "--kubeconfig", KUBECONFIG_FILE, *args], timeout=timeout)
    if check and result.returncode != 0:
        raise AssertionError(f"kubectl {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def get_json(*args: str) -> dict[str, Any]:
    return json.loads(kubectl(*args, "-o", "json").stdout)


def condition_true(resource: dict[str, Any], condition_type: str) -> bool:
    conditions = resource.get("status", {}).get("conditions", [])
    return any(c.get("type") == condition_type and c.get("status") == "True" for c in conditions)
