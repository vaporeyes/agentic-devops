# ABOUTME: Tests the builder harness: permission rules in .claude/settings.json and the audit hook.
# ABOUTME: Each control gets a paired proof where practical (good input recorded, bad input survives).
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
HOOK = REPO_ROOT / ".claude" / "hooks" / "audit.sh"

PROMPTING_MODES = {"default", "acceptEdits", "plan"}
REQUIRED_ASK = {
    "Bash(kubectl apply:*)",
    "Bash(kubectl delete:*)",
    "Bash(kubectl patch:*)",
    "Bash(helm install:*)",
    "Bash(helm upgrade:*)",
    "Bash(argocd app sync:*)",
    "Bash(git push:*)",
}
REQUIRED_DENY = {"Read(**/.env)", "Read(**/credentials*)", "Edit(.claude/**)"}
MUTATING_PREFIXES = (
    "Bash(kubectl apply",
    "Bash(kubectl delete",
    "Bash(helm install",
    "Bash(git push",
)


@pytest.fixture(scope="module")
def permissions() -> dict:
    return json.loads(SETTINGS.read_text())["permissions"]


def test_default_mode_prompts(permissions):
    # bypassPermissions turns every ask rule into a no-op while leaving it in the file.
    assert permissions.get("defaultMode") in PROMPTING_MODES


def test_mutations_require_approval(permissions):
    assert REQUIRED_ASK <= set(permissions["ask"])


def test_no_mutation_is_auto_allowed(permissions):
    allowed = [rule for rule in permissions["allow"] if rule.startswith(MUTATING_PREFIXES)]
    assert allowed == []


def test_secrets_and_harness_are_denied(permissions):
    assert REQUIRED_DENY <= set(permissions["deny"])


def test_hooks_registered_for_pre_and_post_tool_use():
    hooks = json.loads(SETTINGS.read_text())["hooks"]
    for event in ("PreToolUse", "PostToolUse"):
        commands = [h["command"] for entry in hooks[event] for h in entry["hooks"]]
        assert any(command.endswith(".claude/hooks/audit.sh") for command in commands), event


def test_hook_is_executable():
    assert os.access(HOOK, os.X_OK)


def _run_hook(tmp_path: Path, stdin: str) -> list[dict]:
    env = {
        **os.environ,
        "CLAUDE_AUDIT_LOG_DIR": str(tmp_path),
        "CLAUDE_AGENT_IDENTITY": "claude-code-builder-test",
        "CLAUDE_BUILD_PHASE": "0",
    }
    result = subprocess.run(
        [str(HOOK)], input=stdin, env=env, capture_output=True, text=True, timeout=10, check=False
    )
    assert result.returncode == 0, result.stderr
    lines = (tmp_path / "tool-invocations.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def test_hook_records_attributed_event(tmp_path):
    payload = {
        "hook_event_name": "PreToolUse",
        "session_id": "s-1",
        "cwd": "/repo",
        "tool_name": "Bash",
        "tool_input": {"command": "kubectl get nodes"},
    }
    (event,) = _run_hook(tmp_path, json.dumps(payload))
    assert event["agent_identity"] == "claude-code-builder-test"
    assert event["build_phase"] == "0"
    assert event["tool_name"] == "Bash"
    assert event["tool_input"] == {"command": "kubectl get nodes"}
    assert event["timestamp"].endswith("Z")


def test_hook_records_malformed_payload_without_failing(tmp_path):
    (event,) = _run_hook(tmp_path, "not json {")
    assert event["audit_error"] == "failed to parse payload"
    assert event["agent_identity"] == "claude-code-builder-test"
