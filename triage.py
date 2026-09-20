import json
from pathlib import Path

from rules import classify_by_rule
from trace import log_event
from llm import decide_messages


DECISIONS_FILE = Path("decisions.json")

BATCH_SIZE = 10

VALID_DISPOSITIONS = {
    "reply",
    "archive",
    "defer",
    "delegate",
    "escalate",
}


def load_inbox():
    with open("inbox.json", "r", encoding="utf-8") as file:
        return json.load(file)


def rule_triage(message):
    result = classify_by_rule(message)

    if result == "hostile":
        return {
            "message_id": message["id"],
            "disposition": "escalate",
            "reason": (
                "Message contains instructions attempting "
                "to control the assistant; requires human review"
            ),
            "method": "security_rule",
        }

    if result == "archive":
        return {
            "message_id": message["id"],
            "disposition": "archive",
            "reason": "Obvious automated or informational noise",
            "method": "rule",
        }

    return None


def save_decisions(decisions):
    with DECISIONS_FILE.open("w", encoding="utf-8") as file:
        json.dump(decisions, file, indent=2)


def validate_decisions(messages, decisions):
    message_ids = {
        message["id"]
        for message in messages
    }

    decision_ids = [
        decision["message_id"]
        for decision in decisions
    ]

    if len(decision_ids) != len(set(decision_ids)):
        raise ValueError(
            "Duplicate message decisions found"
        )

    if message_ids != set(decision_ids):
        missing = message_ids - set(decision_ids)
        extra = set(decision_ids) - message_ids

        raise ValueError(
            f"Decision mismatch. "
            f"Missing={missing}, Extra={extra}"
        )

    for decision in decisions:
        if decision["disposition"] not in VALID_DISPOSITIONS:
            raise ValueError(
                f"Invalid disposition: "
                f"{decision['disposition']}"
            )

        if not decision.get("reason"):
            raise ValueError(
                f"Missing reason for "
                f"{decision['message_id']}"
            )


def run_r1():
    messages = load_inbox()

    decisions = []
    model_messages = []

    rule_handled = 0

    # First use deterministic rules.
    for message in messages:
        decision = rule_triage(message)

        if decision is not None:
            rule_handled += 1

            decisions.append(decision)

            log_event({
                "event": "decision",
                "cap": "R1",
                "message_id": decision["message_id"],
                "disposition": decision["disposition"],
                "reason": decision["reason"],
                "method": decision["method"],
            })

        else:
            model_messages.append(message)

    # Use the LLM for messages that need reasoning.
    model_handled = 0

    for start in range(
        0,
        len(model_messages),
        BATCH_SIZE,
    ):
        batch = model_messages[
            start:start + BATCH_SIZE
        ]

        batch_number = start // BATCH_SIZE + 1

        print(
            f"Processing model batch "
            f"{batch_number}: {len(batch)} messages"
        )

        results = decide_messages(batch)

        for result in results:
            decision = {
                "message_id": result["message_id"],
                "disposition": result["disposition"],
                "reason": result["reason"],
                "method": "llm",
            }

            decisions.append(decision)

            model_handled += 1

            log_event({
                "event": "decision",
                "cap": "R1",
                "message_id": decision["message_id"],
                "disposition": decision["disposition"],
                "reason": decision["reason"],
                "method": "llm",
            })

    # Verify that every inbox message has exactly one decision.
    validate_decisions(
        messages,
        decisions,
    )

    # Keep decisions in the same order as inbox.json.
    decision_map = {
        decision["message_id"]: decision
        for decision in decisions
    }

    decisions = [
        decision_map[message["id"]]
        for message in messages
    ]

    save_decisions(decisions)

    return {
        "messages": len(messages),
        "rule_handled": rule_handled,
        "model_handled": model_handled,
        "decisions": decisions,
    }
