# ABOUTME: Unit tests for the phase evidence record builder.
# ABOUTME: Covers required fields, dirty-tree refusal, and absence of payload fields.
import pytest
from record_evidence import build_record

BASE = {
    "phase": 0,
    "git_revision": "9d7f2a1c",
    "git_dirty": False,
    "kube_context": "kind-agentic",
    "server_version": "v1.35.0",
    "components_sha256": "ab" * 32,
    "gate_result": "passed",
}


def test_record_contains_required_fields():
    record = build_record(**BASE, extra={})
    for field in (
        "phase",
        "git_revision",
        "kube_context",
        "server_version",
        "components_sha256",
        "gate_result",
        "recorded_at",
    ):
        assert record.get(field) not in (None, ""), field
    assert record["recorded_at"].endswith("+00:00")


def test_dirty_tree_is_refused():
    with pytest.raises(ValueError, match="dirty"):
        build_record(**{**BASE, "git_dirty": True}, extra={})


def test_failed_gate_is_refused():
    with pytest.raises(ValueError, match="gate"):
        build_record(**{**BASE, "gate_result": "failed"}, extra={})


def test_payload_like_extra_fields_are_refused():
    with pytest.raises(ValueError, match="prompt"):
        build_record(**BASE, extra={"prompt": "ignore previous instructions"})


def test_extra_identifiers_are_kept():
    record = build_record(**BASE, extra={"trace_id": "4bf92f3577b34da6"})
    assert record["trace_id"] == "4bf92f3577b34da6"
