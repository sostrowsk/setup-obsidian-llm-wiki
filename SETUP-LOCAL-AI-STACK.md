# The Local AI Stack — Overview of the Four Repositories

A fully local, offline-capable AI infrastructure for **Debian** and **macOS (Apple Silicon)**: model serving, a chat & RAG frontend, an autonomous agent with long-term memory, and an LLM-maintained knowledge wiki. Every layer runs on your own hardware — **no cloud APIs, no API keys, no telemetry**; internet is only needed once, during provisioning. Each repository ships a manual **runbook** (with the pitfalls actually hit) plus an idempotent **Ansible playbook**.

This file is identical in all four repositories.

## The four repositories

| Repository | Layer | What it provides |
|---|---|---|
| [setup-local-llm](https://github.com/sostrowsk/setup-local-llm) | **Models** | The model fleet: one `llama-server` per model, OpenAI-compatible, fixed ports — Qwen 3.6 35B-A3B chat (:8084), Qwen3-Embedding-8B (:8085), verified Qwen3-Reranker-8B (:8086), Gemma 4 12B/26B-MoE/31B (:8087–:8089), Whisper (:8090 Debian / mlx-whisper macOS) |
| [setup-open-webui](https://github.com/sostrowsk/setup-open-webui) | **Frontend** | Open WebUI natively (uv venv, Python 3.11, no Docker) on :8080 — chat on the fleet, hybrid RAG (BM25 + vectors + external reranker), built-in local Whisper STT, declarative env-file config |
| [setup-hermes-honcho](https://github.com/sostrowsk/setup-hermes-honcho) | **Agent + memory** | Hermes Agent (Nous Research) with self-hosted Honcho (Theory-of-Mind memory) on native PostgreSQL/pgvector — Honcho API :8000, its own minimal LLM serving on :8001/:8002 (Debian llama.cpp / macOS vllm-mlx) |
| [setup-obsidian-llm-wiki](https://github.com/sostrowsk/setup-obsidian-llm-wiki) | **Knowledge** | An LLM-maintained wiki (Karpathy pattern): `raw/` sources → condensed, cross-linked `wiki/` pages, governed by `CLAUDE.md`; Obsidian as viewer, Claude Code or a local agent (Hermes) as maintainer; deterministic lint |

## Architecture

```
                        ┌───────────────────────────────────────────────┐
                        │  Model layer (setup-local-llm)                │
  Open WebUI :8080 ────►│  :8084 Qwen3.6-35B-A3B-Q8_0   (chat, 64K ctx) │
  (setup-open-webui)    │  :8085 Qwen3-Embedding-8B     (embeddings)    │
        chat/RAG/STT    │  :8086 Qwen3-Reranker-8B      (/v1/rerank)    │
                        │  :8087–:8089 Gemma 4 12B/26B-A4B/31B (chat)   │
  Hermes Agent ────────►│  :8090 whisper-server (Debian)                │
  (setup-hermes-honcho) └───────────────────────────────────────────────┘
        │ memory                    ▲
        ▼                           │ retrieval / maintainer LLM
  Honcho API :8000                  │
  PostgreSQL :5432 (pgvector)   LLM wiki vault ~/llm-wiki + Obsidian
                                (setup-obsidian-llm-wiki)
```

All model endpoints are OpenAI-compatible (`/v1/...`), the **model name = the server `--alias`**, and API-key fields take any dummy value (llama.cpp ignores them).

## How the layers compose

- **Open WebUI → fleet:** chat backends `:8084` (+ Gemma ports when served), RAG embeddings `:8085`, external reranker `:8086/v1/rerank` (full URL required).
- **Hermes → LLM serving, two options:** (a) the self-contained serving that setup-hermes-honcho provisions itself (chat `:8001`, embeddings `:8002`); or (b) point Hermes/Honcho at the fleet instead (`model.base_url http://HOST:8084/v1`, embedding blocks → `:8085`) and skip the duplicate serving. Hermes' hard requirements hold either way: **≥ 64K context** and working **tool calling** on the chat endpoint.
- **Honcho ↔ embeddings:** `EMBEDDING_VECTOR_DIMENSIONS` must exactly match the serving model and must be set **before** the first DB migration (Qwen3-Embedding-0.6B: 1024; Qwen3-Embedding-8B: 4096 by default).
- **LLM wiki → everything:** Obsidian plugins (Copilot/Smart Connections) use `:8084`/`:8085` for in-vault retrieval; the wiki *maintainer* is Claude Code (cloud) or Hermes (fully local). Open WebUI is the chat/RAG frontend, not the wiki maintainer.

## Recommended install order

1. **setup-local-llm** — models + endpoints (verify: `verify_endpoints.sh`, incl. the reranker sanity check and tool-calling test).
2. **setup-open-webui** — frontend on the fleet (verify: `verify_openwebui.sh`).
3. **setup-hermes-honcho** — agent + memory; decide serving option (a) or (b) above before running.
4. **setup-obsidian-llm-wiki** — vault + Obsidian; bootstrap ingest is LLM work (Claude Code or Hermes).

1–2 and 3–4 are independent pairs; only the model endpoints must exist before their consumers.

## Shared conventions

- `127.0.0.1` = machine-local, `0.0.0.0` = LAN exposure (then add auth where supported — e.g. Honcho `USE_AUTH`).
- Services: **systemd user units** + `loginctl enable-linger` (Debian) / **launchd agents** or start scripts (macOS).
- Ansible: OS switch via `ansible_facts['os_family']`, idempotent, `ansible.builtin` only; existing data (vaults, databases, downloads) is never overwritten.
- **No secrets in any repo** — dummy API keys throughout; the only real secret (Honcho DB password) is supplied at runtime.

## Port map

| Port | Service | Repo |
|---|---|---|
| 5432 | PostgreSQL (pgvector) | setup-hermes-honcho |
| 8000 | Honcho API | setup-hermes-honcho |
| 8001 / 8002 | Hermes' own minimal chat / embeddings serving (option a) | setup-hermes-honcho |
| 8080 | Open WebUI | setup-open-webui |
| 8084–8089 | Model fleet: chat / embeddings / reranker / Gemma | setup-local-llm |
| 8090 | whisper-server (Debian) | setup-local-llm |
