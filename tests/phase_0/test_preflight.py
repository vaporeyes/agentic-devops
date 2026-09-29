# ABOUTME: Phase 0 gate: proves the target cluster and repository match the declared start state.
# ABOUTME: Read-only; installs nothing. See spec/phases/phase-0-preflight.md.
import re
import subprocess

import yaml
from check_components import validate
from conftest import REPO_ROOT, condition_true, get_json, kubectl


def _components() -> dict:
    return yaml.safe_load((REPO_ROOT / "components.yaml").read_text())


def _minor(version: str) -> tuple[int, int] | None:
    match = re.search(r"v?(\d+)\.(\d+)", version)
    return (int(match.group(1)), int(match.group(2))) if match else None


def test_at_least_one_node_ready():
    nodes = get_json("get", "nodes")["items"]
    ready = [n["metadata"]["name"] for n in nodes if condition_true(n, "Ready")]
    assert ready, "no Ready nodes"


def test_server_version_meets_floor():
    floor = _minor(_components()["metadata"]["kubernetes_min_minor"])
    server = get_json("version").get("serverVersion", {})
    actual = _minor(server.get("gitVersion", ""))
    assert actual is not None, f"unreadable serverVersion: {server!r}"
    assert actual >= floor, f"server {server.get('gitVersion')} below floor {floor}"


def test_argocd_namespace_absent():
    result = kubectl("get", "namespace", "argocd", check=False)
    assert result.returncode != 0, "argocd namespace exists; cluster is not bare"


def test_no_argocd_applications():
    # On a bare cluster the CRD is absent and the lookup fails; either way, no Applications.
    result = kubectl("get", "applications.argoproj.io", "-A", "-o", "name", check=False)
    assert result.returncode != 0 or not result.stdout.strip(), result.stdout


def test_components_valid_and_pinned():
    assert validate(_components()) == []


def test_repository_at_clean_committed_revision():
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert head.returncode == 0, "repository has no commits; record a starting revision"
    status = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert status.stdout.strip() == "", f"working tree is dirty:\n{status.stdout}"
