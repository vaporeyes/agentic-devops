# Phase 5: Model Serving Behind the Gateway

**Goal:** An OpenAI-compatible model endpoint served in-cluster, reachable
by clients only through agentgateway, with its runtime contract locked by
tests.

This phase precedes agent runtime (the book's order is reversed) so that
Phase 6 gates exercise real inference.

**Inputs:** Phase 4 passed.

**Outputs:**

- KServe CRDs then controller (v0.19.0)
- `platform/2-ai-plane/vllm/base` plus per-profile overlays using JSON
  patches (never strategic merge on the InferenceService)
- Argo CD ignore rule scoped to the one normalized `deploymentMode`
  annotation
- AgentgatewayBackend and HTTPRoute for `/v1` to the predictor
- NetworkPolicy: predictor accepts traffic only from the gateway and
  observability

**Test criteria (`tests/phase_5/`):**

- `PredictorReady=True` (internal topology leaves top-level Ready False)
- Live pod runtime contract: KV cache, memory limit, `/dev/shm` size,
  `HOME`/`USER`, numeric UID, `SYS_NICE` only, tool-call flags, no
  `--device`
- `/v1/models` via the gateway returns `qwen3-1.7b`
- Chat completion via the gateway returns the served model name
- `tool_choice=auto` request returns 200
- Direct predictor access from the `kagent` namespace is refused
- Warm latency sample under the recorded threshold; evidence records image
  digest, median, and max

**Profile notes:**

- `eks`: book-verified CPU settings (4/6 CPU, 10Gi/16Gi, KV cache 2,
  `/dev/shm` 4Gi) on a node with at least 32Gi.
- We build our own vLLM CPU image (decided 2026-09-29): multi-arch
  (`linux/arm64` and `linux/amd64`) from the pinned vLLM v0.23.0 source,
  weights baked, offline mode, published to our registry, signed, with an
  SBOM, and referenced by digest. The same image serves `local` on Apple
  Silicon and allows Graviton node pools on `eks`.
- Image build acceptance: `id` reports UID 1001 able to traverse the app
  and cache paths; `/v1/models` returns `qwen3-1.7b` with no network; a
  `tool_choice=auto` request returns 200; `--device` is not required.
- CPU and memory settings are re-measured per architecture; the x86 values
  above are not assumed to hold on arm64.

**Completion promise:** `<promise>PHASE5_DONE</promise>`

**Stop here.**
