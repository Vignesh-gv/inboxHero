import json
import os

import ollama
from dotenv import load_dotenv

from retrieval import get_earlier_messages
from trace import log_event


load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b")


def draft_reply(message):
    earlier_messages = get_earlier_messages(message)

    if not earlier_messages:
        return None

    evidence = []

    for item in earlier_messages:
        evidence.append({
            "id": item["id"],
            "from": item["from"],
            "subject": item["subject"],
            "body": item["body"],
        })

        log_event({
            "event": "read",
            "cap": "R2",
            "message_id": item["id"],
        })

    prompt = f"""
You are drafting a reply to an email.

CURRENT EMAIL:
{json.dumps(message, ensure_ascii=False)}

EARLIER MESSAGES FROM THE SAME THREAD:
{json.dumps(evidence, ensure_ascii=False)}

Use ONLY the earlier messages as factual evidence.

If the earlier messages do not contain enough information to answer,
return:

{{
  "draft": null,
  "cited_ids": []
}}

Otherwise return:

{{
  "draft": "short professional reply",
  "cited_ids": ["message_id"]
}}

IMPORTANT RULES:

- Never invent information.
- cited_ids must contain only IDs from the earlier messages.
- Never expose passwords, API keys, tokens, or credentials.
- If the requested information is a credential, do not reproduce it.
- Instead, suggest sharing the information through a secure channel.
- Return JSON only.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
    )

    result = json.loads(
        response["message"]["content"]
    )

    cited_ids = result.get(
        "cited_ids",
        []
    )

    valid_ids = {
        item["id"]
        for item in earlier_messages
    }

    if not set(cited_ids).issubset(valid_ids):
        raise ValueError(
            "Draft cites a message that was not retrieved"
        )

    draft = result.get("draft")

    if draft:
        log_event({
            "event": "draft",
            "cap": "R2",
            "message_id": message["id"],
            "cited_ids": cited_ids,
            "draft": draft,
        })

    return result
