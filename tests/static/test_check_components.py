# ABOUTME: Unit tests for the components.yaml validator, including the real manifest.
# ABOUTME: Each rule has a failing case so a weakened validator is caught.
from pathlib import Path

import pytest
import yaml
from check_components import validate

REPO_ROOT = Path(__file__).resolve().parents[2]


def _component(**overrides) -> dict:
    base = {
        "name": "x",
        "plane": "ai",
        "profiles": ["local"],
        "install_method": "helm",
        "chart_repo": "https://example.invalid/charts",
        "chart_version": "1.0.0",
        "app_version": "1.0.0",
        "phase": 1,
    }
    return {**base, **overrides}


def _errors(*components: dict) -> list[str]:
    return validate({"components": list(components)})


def test_real_manifest_is_valid():
    data = yaml.safe_load((REPO_ROOT / "components.yaml").read_text())
    assert validate(data) == []


def test_valid_component_has_no_errors():
    assert _errors(_component()) == []


def test_empty_manifest_is_reported():
    assert validate({"components": []}) == ["components.yaml has no components"]


def test_missing_components_key_is_reported():
    assert validate({}) == ["components.yaml has no components"]


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"app_version": ""}, "x: missing app_version"),
        ({"chart_version": None}, "x: helm install without a pinned chart_version"),
        ({"chart_repo": None}, "x: helm install without a chart_repo"),
        ({"plane": "control"}, "x: plane 'control' not in"),
        ({"install_method": "curl-pipe-bash"}, "x: install_method 'curl-pipe-bash' not in"),
        ({"profiles": []}, "x: profiles must be a non-empty list"),
        ({"profiles": ["local", "gke"]}, "x: unknown profiles ['gke']"),
        ({"phase": 9}, "x: phase must be an integer 0-8"),
        ({"phase": "1"}, "x: phase must be an integer 0-8"),
    ],
)
def test_rule_violations_are_reported(overrides, expected):
    errors = _errors(_component(**overrides))
    assert any(error.startswith(expected) for error in errors), errors


def test_non_helm_component_needs_no_chart_version():
    component = _component(install_method="kubectl", chart_repo=None, chart_version=None)
    assert _errors(component) == []


def test_duplicate_names_are_reported():
    assert "x: duplicate name" in _errors(_component(), _component())


def test_bundled_without_version_is_reported():
    component = _component(bundled=[{"name": "sub-a", "version": "2.0"}, {"name": "sub-b"}])
    errors = _errors(component)
    assert "x: bundled sub-b missing version" in errors
    assert not any("sub-a" in error for error in errors)


def test_all_errors_reported_in_one_run():
    errors = _errors(_component(name="a", app_version=""), _component(name="b", plane=""))
    assert any(error.startswith("a:") for error in errors)
    assert any(error.startswith("b:") for error in errors)
