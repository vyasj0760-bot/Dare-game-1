# OpenAmika brain integration review

Reviewed upstream repository: https://github.com/zeekk0/OpenAmika
Reviewed source modules: `brain/f_bridge.py`, `f_memory.py`, `f_extract.py`,
`f_roles.py`, `f_openrouter.py`, `f_usage.py`, `f_settle.py`,
`f_method.py`, `po_contract.py`, `brain/PROTOCOL.md`, and configuration files.

## What can be reused

- The upstream Python brain orchestration and turn/history design in `f_bridge.py`.
- The fact extraction and memory runtime algorithms in `f_extract.py` and `f_memory.py`.
- The provider transport/metering abstractions in `f_openrouter.py`, `f_roles.py`, and `f_usage.py`.
- The emotion/output parsing contract in `po_contract.py`, after defining Mira's own emotion vocabulary and output format.

## Why it is not a drop-in library

The bridge is not a standalone callable LLM module. `f_bridge.install(g)` expects a host application context and a complete set of runtime services/routes. It reads configuration from the upstream repository layout, loads persona templates and scenes, and wires provider roles, billing, memory workers, and background lifecycle behavior. The memory runtime expects injected extraction and embedding callbacks; upstream's checked-in `config/build_f.json` defaults embeddings to a local BGE-M3 service at `127.0.0.1:8011`. That local embedding service is not included in this starter and is not a suitable assumption for a free CPU-only cloud host.

The upstream project README targets Windows + NVIDIA RTX hardware for its full product. Its frontend/speech/Live2D stack is not part of Mira's cloud-brain target.

## Safe integration decision

Do not copy only `f_bridge.py` or pretend it is connected. Do not copy Amika's persona text, name, likeness, voice, Live2D files, or model assets. Keep the transport scaffold honest until the host-context and embedding/provider adapters are implemented and tested.

Next engineering stage:
1. Build a minimal Mira host adapter for the subset of `g` dependencies used by the chosen bridge entry points.
2. Replace the local BGE-M3 embedding dependency with a supported remote embedding provider or a small external embedding service; test cost and latency before selecting.
3. Set a Mira-specific persona, Indian timezone, Hindi/Hinglish response rules, and safe emotion labels. Do not reuse Amika's default character prompts.
4. Move durable memory away from Render's ephemeral filesystem to a database/object store; verify the memory runtime's snapshot and vector-sidecar consistency.
5. Add unit/integration tests for fresh conversation, history recall, restart persistence, interruption, and provider failure.
6. Only then switch the Socket.IO adapter from the placeholder to the real brain.

## Cost warning

Render's free web service does not make model inference or embeddings free. Do not add a provider key until the user has selected a provider and reviewed any billing/usage limits. Keep all secrets in host environment variables, never in Git.
