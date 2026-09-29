#!/usr/bin/env bash
# ABOUTME: Claude Code PreToolUse/PostToolUse hook that appends one JSON line per tool call.
# ABOUTME: Records agent identity, build phase, and timestamp; never fails the session.
set -uo pipefail

LOG_DIR="${CLAUDE_AUDIT_LOG_DIR:-${CLAUDE_PROJECT_DIR:-.}/.claude/audit}"
LOG_FILE="${LOG_DIR}/tool-invocations.jsonl"
AGENT_IDENTITY="${CLAUDE_AGENT_IDENTITY:-claude-code-builder-unset}"
BUILD_PHASE="${CLAUDE_BUILD_PHASE:-unset}"

mkdir -p "${LOG_DIR}" || exit 0

payload="$(cat)"

record_error() {
  jq -cn --arg agent "${AGENT_IDENTITY}" --arg phase "${BUILD_PHASE}" --arg err "$1" \
    '{timestamp: (now | todate), agent_identity: $agent, build_phase: $phase, audit_error: $err}' \
    >>"${LOG_FILE}" 2>/dev/null ||
    printf '{"agent_identity":"%s","build_phase":"%s","audit_error":"%s"}\n' \
      "${AGENT_IDENTITY}" "${BUILD_PHASE}" "$1" >>"${LOG_FILE}"
}

if ! command -v jq >/dev/null 2>&1; then
  printf '{"agent_identity":"%s","build_phase":"%s","audit_error":"jq not found on PATH"}\n' \
    "${AGENT_IDENTITY}" "${BUILD_PHASE}" >>"${LOG_FILE}"
  exit 0
fi

# PostToolUse carries the result in tool_response.
printf '%s' "${payload}" | jq -c \
  --arg agent "${AGENT_IDENTITY}" \
  --arg phase "${BUILD_PHASE}" \
  '{
     timestamp: (now | todate),
     agent_identity: $agent,
     build_phase: $phase,
     hook_event_name: .hook_event_name,
     session_id: .session_id,
     cwd: .cwd,
     tool_name: .tool_name,
     tool_input: .tool_input,
     tool_response: .tool_response
   }' >>"${LOG_FILE}" 2>/dev/null || record_error "failed to parse payload"

exit 0
