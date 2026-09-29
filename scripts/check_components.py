# ABOUTME: Validates components.yaml: every component pinned, well-formed, and profile-scoped.
# ABOUTME: Reports every violation in one run and exits nonzero when any exist.
"""Validate the pinned component inventory.

Usage:
    uv run --group test python scripts/check_components.py [path]
"""

import sys
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

PLANES = frozenset({"foundation", "ai", "self-service"})
PROFILES = frozenset({"local", "eks"})
INSTALL_METHODS = frozenset({"helm", "helm-oci", "kustomize", "kubectl", "library"})
HELM_METHODS = frozenset({"helm", "helm-oci"})
MAX_PHASE = 8


def _component_errors(component: dict[str, Any]) -> Iterator[str]:
    """Yield rule violations for a single component entry."""
    name = component.get("name") or "<unnamed>"

    if not component.get("app_version"):
        yield f"{name}: missing app_version"

    plane = component.get("plane")
    if plane not in PLANES:
        yield f"{name}: plane {plane!r} not in {sorted(PLANES)}"

    method = component.get("install_method")
    if method not in INSTALL_METHODS:
        yield f"{name}: install_method {method!r} not in {sorted(INSTALL_METHODS)}"

    if method in HELM_METHODS:
        if not component.get("chart_version"):
            yield f"{name}: helm install without a pinned chart_version"
        if not component.get("chart_repo"):
            yield f"{name}: helm install without a chart_repo"

    profiles = component.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        yield f"{name}: profiles must be a non-empty list"
    else:
        unknown = sorted(set(profiles) - PROFILES)
        if unknown:
            yield f"{name}: unknown profiles {unknown}"

    phase = component.get("phase")
    if not isinstance(phase, int) or isinstance(phase, bool) or not 0 <= phase <= MAX_PHASE:
        yield f"{name}: phase must be an integer 0-{MAX_PHASE}, got {phase!r}"

    for item in component.get("bundled") or []:
        if not item.get("version"):
            yield f"{name}: bundled {item.get('name') or '<unnamed>'} missing version"


def validate(data: dict[str, Any]) -> list[str]:
    """Return human-readable errors for the manifest; empty when valid.

    Args:
        data: Parsed components.yaml document.

    Returns:
        One error string per violation, across all components.
    """
    components = data.get("components") or []
    if not components:
        return ["components.yaml has no components"]

    name_counts = Counter(component.get("name") for component in components)
    duplicates = [f"{name}: duplicate name" for name, count in name_counts.items() if count > 1]
    return duplicates + [
        error for component in components for error in _component_errors(component)
    ]


def main(path: str = "components.yaml") -> int:
    """Validate the manifest at path and print the result."""
    manifest = Path(path)
    if not manifest.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    data = yaml.safe_load(manifest.read_text()) or {}
    errors = validate(data)
    if errors:
        print("components.yaml failed validation:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"components.yaml is valid: {len(data['components'])} components, all pinned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
