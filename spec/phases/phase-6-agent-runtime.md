# Phase 6: Agent Runtime, Tools, Guardrail, Telemetry

**Goal:** A reconciled kagent Agent whose model, tools, guardrail, and trace
path are explicit and proven.

**Inputs:** Phase 5 passed.

**Outputs:**

- kagent CRDs then controller (v0.9.9), agent tracing enabled
- `platform-helper` Agent (read-only system message, guardrail annotation)
- ModelConfig pointing at the gateway, not the predictor (closes a book gap)
- MCP: KMCP server, AgentgatewayBackend with `spec.mcp.targets`, `/mcp`
  HTTPRoute, RemoteMCPServer via the gateway (Streamable HTTP), named tool
  binding with an approval list (closes a book gap)
- `/agents/<name>` HTTPRoute with URL rewrite to the per-agent Service on
  port 8080; invocation body pinned from the agent card (A2A JSON-RPC)
- Guardrail: `adapters/guardrail-webhook/` implementing the agentgateway
  guardrail webhook contract (`/request`, `/response`) in front of the
  selected scanner, plus the AgentgatewayPolicy with explicit
  `failureMode: FailClosed` (closes a book gap)
- OpenLLMetry probe pinned with `traceloop-sdk 0.61.0` and `openai 1.109.1`

**Guardrail scanner decision (required before building):** LLM Guard is
archived upstream and cannot receive security fixes. Select a maintained
scanner, add it to `components.yaml` with a pinned version, and keep the
adapter contract scanner-agnostic.

**Test criteria (`tests/phase_6/`):**

- Agent Ready for the current `metadata.generation`
- RemoteMCPServer Accepted with discovered tools; Agent binds exactly the
  approved names and approval list
- Injection paired proof: hostile fixture returns 400/403, benign returns
  200 through the same route (503 on both fails)
- A tool call through the gateway produces an access-log event naming
  server, tool, outcome, and trace ID
- A gen_ai span for the requested model is searchable in Tempo; the test
  drives its own traffic first
- Adapter unit tests: pass, reject, and scanner-error mapped to reject

**Completion promise:** `<promise>PHASE6_DONE</promise>`

**Stop here.**
