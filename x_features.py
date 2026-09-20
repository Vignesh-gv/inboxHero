import json
import re

from datetime import datetime
from pathlib import Path
from trace import log_event

OWNER = "sam@paperjet.io"


def load_inbox():
    return json.loads(
        Path("inbox.json").read_text(
            encoding="utf-8"
        )
    )


def follow_up_tracking():
    """
    X1:
    Find messages sent by the owner that have not received
    a response after at least three days.
    """

    messages = load_inbox()

    latest_time = max(
        datetime.fromisoformat(
            message["timestamp"]
        )
        for message in messages
    )

    results = []

    for message in messages:

        if message["from"].lower() != OWNER:
            continue

        thread = [
            item
            for item in messages
            if item["thread_id"]
            == message["thread_id"]
        ]

        answered = any(
            item["timestamp"] > message["timestamp"]
            and item["from"].lower() != OWNER
            for item in thread
        )

        if answered:
            continue

        sent_time = datetime.fromisoformat(
            message["timestamp"]
        )

        days_waiting = (
            latest_time - sent_time
        ).days

        if days_waiting >= 3:
            results.append({
                "message_id": message["id"],
                "days_waiting": days_waiting,
                "draft": (
                    "Hi, just following up on my earlier "
                    f"email about '{message['subject']}'. "
                    "Please let me know when you have an update."
                ),
            })

    log_event({
        "event": "follow_up_tracking",
        "cap": "X1",
        "count": len(results),
    })

    return results


def morning_digest():
    """
    X2:
    Group triage decisions into three useful categories.
    """

    decisions = json.loads(
        Path("decisions.json").read_text(
            encoding="utf-8"
        )
    )

    needs_me = [
        decision
        for decision in decisions
        if decision["disposition"]
        in {"reply", "escalate"}
    ]

    can_wait = [
        decision
        for decision in decisions
        if decision["disposition"]
        in {"defer", "delegate"}
    ]

    archived = [
        decision
        for decision in decisions
        if decision["disposition"]
        == "archive"
    ]

    digest = {
        "needs_me": needs_me,
        "can_wait": can_wait,
        "auto_archived_count": len(archived),
    }

    log_event({
        "event": "morning_digest",
        "cap": "X2",
    })

    return digest


def deadline_scan():
    """
    X3:
    Find messages that mention a deadline or date requirement.
    """

    messages = load_inbox()

    pattern = re.compile(
        r"\b(?:by|before|due|deadline|on)\s+"
        r"(?:the\s+)?"
        r"\d{1,2}"
        r"(?:st|nd|rd|th)?\b",
        re.IGNORECASE,
    )

    results = []

    for message in messages:

        text = (
            message["subject"]
            + " "
            + message["body"]
        )

        if pattern.search(text):
            results.append({
                "message_id": message["id"],
                "subject": message["subject"],
            })

    log_event({
        "event": "deadline_scan",
        "cap": "X3",
        "count": len(results),
    })

    return results
