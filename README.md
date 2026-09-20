# inboxHero

An agentic local inbox assistant that processes a mock inbox from unread to empty while keeping human approval around irreversible actions.

## Student

**Name:** Vignesh  
**Certificate / Roll Number:** `cert-aai-2026-06-0062`

## Repository

`https://github.com/Vignesh-gv/inboxHero.git`

---

# Project Overview

inboxHero processes a local mock email inbox stored in `inbox.json`.

For every message, the system decides what should happen:

- reply
- archive
- defer
- delegate
- escalate

The system also supports grounded reply drafting, irreversible-action gating, persistent user preferences, hostile-instruction refusal, a three-pane dashboard, and custom capabilities.

No real emails are sent.

Sending is simulated by writing to the local `outbox/` directory.

---

# Architecture

```text
                    inbox.json
                        |
                        v
                +---------------+
                |   inboxHero    |
                +---------------+
                        |
              +---------+---------+
              |                   |
              v                   v
       Deterministic Rules      Ollama
              |                gemma4:12b
              |                   |
              +---------+---------+
                        |
                        v
                 Triage Decisions
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
     Replies          Actions        Dashboard
        |               |                |
        v               v                v
   Grounded Draft    R3 Gate        dashboard.html
                        |
                  +-----+-----+
                  |           |
                  v           v
               Dry-run     Approval
```
