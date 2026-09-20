# inboxHero — Capability Manifest

## Student

**Name:** Vignesh  
**Certificate / Roll Number:** cert-aai-2026-06-0062

## Repository

`https://github.com/Vignesh-gv/inboxHero.git`

---

# System Overview

inboxHero is a local agentic inbox-processing system.

It reads a mock `inbox.json`, classifies every message, produces grounded drafts where appropriate, gates irreversible actions, persists user preferences, refuses hostile embedded instructions, and generates a human-readable dashboard.

The project uses no external agent framework.

**Framework:** none

**Model:** Ollama `gemma4:12b`

**Inbox size:** 100 messages

**Deterministic rule handling:** 35 messages

**LLM handling:** 65 messages

**Retrieval:** thread-walk over the local mail store

**Irreversible actions:** send and delete

**Gate:** per-action human approval or dry-run

---

# Required Capabilities

## R1 — Zero the Inbox

**Tier:** B

### Claim

Every inbox message receives exactly one disposition and a one-line reason.

Allowed dispositions are:

- `reply`
- `archive`
- `defer`
- `delegate`
- `escalate`

### Command

```bash
python demo.py --cap R1
```
