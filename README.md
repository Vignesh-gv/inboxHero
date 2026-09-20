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

Technology

- Python
- Ollama
- gemma4:12b
- No agent framework

Configuration
Model configuration is loaded through config.py.
Environment variables are stored in **.env** locally and are not committed or submitted.
The repository includes **.env.example** as the configuration template.

# Example:

    GEMINI_API_KEY=
    GEMINI_MODEL=
    OLLAMA_MODEL=gemma4:12b

The current implementation uses **Ollama** and **gemma4:12b**.

# Setup

1. Install Python dependencies
   **python -m pip install -r requirements.txt**

2. Make sure Ollama is running
   **ollama list**

3. Environment configuration
   **Create .env from .env.example if required.**

# Capability Manifest

The complete capability manifest is available in: **CAPABILITIES.md**
Machine-readable capability information is available in: **capabilities.json**

# Safety and Trust Boundaries

Email content is treated as untrusted data.
Instructions contained inside an email are not treated as system instructions.
Hostile or social-engineering messages are refused and flagged.
Irreversible operations such as sending and deleting are protected by the R3 gate.
The mock inbox is not modified by the delete demonstration.

# Final Report

1. What did you refuse to automate?
   inboxHero deliberately refuses to act on hostile messages such as m017, which contains an embedded directive telling an automated agent to reply to unread messages and hide the action from the user. The message is detected by rules.py and handled by security.py as a refusal rather than being executed as an instruction. The system also refuses to perform irreversible actions such as sending or deleting without the R3 gate. The boundary is drawn where email content attempts to control the agent or where an action could create an irreversible external effect.

2. Where does untrusted text enter your system?
   Untrusted text enters through the fields of inbox.json, including the subject and body of every message. The architecture passes these fields to rule classification, retrieval and model processing as message data, while system behavior is implemented by Python components such as rules.py, security.py, triage.py and actions.py. An attacker would therefore need to defeat the security classification and the application-level action gate before their email content could cause an irreversible action. The R3 gate remains outside the email content and requires dry-run mode or explicit human approval.

3. Who is accountable when it sends the wrong thing?
   The owner remains accountable for an approved send because inboxHero requires a human approval decision before performing the irreversible send operation. The actions.py component records the message ID, recipient and approval or rejection decision in trace.jsonl, while the generated message is stored in outbox/. For a grounded reply, draft.py also records the cited message IDs used to construct the draft. These records provide a trace from the source messages and draft through the human gate and final local outbox artifact.

4. Name your own machinery.
   triage.py acts as the main router, llm.py provides the model-based decision component, draft.py and the capability functions in x_features.py act like task-level operations, and the combination of these modules forms the overall crew-like workflow. rules.py, retrieval.py, security.py, preferences.py and actions.py provide supporting machinery that would normally be supplied or coordinated by an agent framework. A framework could have provided standardized agent/task orchestration, routing and state handling, but this project implements those boundaries explicitly so that the security gate and local evidence flow remain easy to inspect. For this assignment, using no framework keeps the implementation small and makes the behavior of each graded capability directly visible in the source code.

# Project Structure

inboxHero/
│
├── inbox.json
├── demo.py
├── config.py
├── rules.py
├── trace.py
├── llm.py
├── triage.py
├── retrieval.py
├── draft.py
├── actions.py
├── preferences.py
├── security.py
├── dashboard.py
├── x_features.py
│
├── capabilities.json
├── CAPABILITIES.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore

# Submission

The final submission is a single ZIP file named: **inboxHero_Vignesh.zip**
