import json
from pathlib import Path

from trace import log_event


def load_decisions():
    return json.loads(
        Path("decisions.json").read_text(
            encoding="utf-8"
        )
    )


def generate_dashboard():
    decisions = load_decisions()

    flagged_ids = {
        "m017",
        "m024",
        "m039",
        "m047",
    }

    pending = []

    for decision in decisions:
        if decision["message_id"] in flagged_ids:
            continue

        if decision["disposition"] in {
            "reply",
            "defer",
            "delegate",
            "escalate",
        }:
            pending.append({
                "message_id": decision["message_id"],
                "proposed_action": decision["disposition"],
                "why_human_needed": decision["reason"],
            })

    flagged = []

    for decision in decisions:
        if decision["message_id"] in flagged_ids:
            flagged.append({
                "message_id": decision["message_id"],
                "attempted_action": (
                    "Embedded instructions attempted "
                    "to control the assistant"
                ),
                "what_system_did": "Refused and escalated for human review",
            })

    commitments = [
        {
            "text": (
                "Board deck must be finished and circulated "
                "two days before the board review."
            ),
            "source_ids": [
                "m038",
                "m040",
            ],
        },
        {
            "text": "Launch target is the 20th.",
            "source_ids": [
                "m026",
                "m036",
            ],
        },
        {
            "text": (
                "CONFLICT: Investor intro and dental cleaning "
                "are both scheduled for 2026-09-15 at 15:00."
            ),
            "source_ids": [
                "m010",
                "m061",
            ],
        },
    ]

    dashboard_data = {
        "pending_actions": pending,
        "flagged": flagged,
        "commitments": commitments,
    }

    pending_html = "".join(
        f"""
        <li>
            <strong>{item['message_id']}</strong>:
            {item['proposed_action']}
            — Human needed: {item['why_human_needed']}
        </li>
        """
        for item in pending
    )

    flagged_html = "".join(
        f"""
        <li>
            <strong>{item['message_id']}</strong>:
            Attempted action:
            {item['attempted_action']}
            — System response:
            {item['what_system_did']}
        </li>
        """
        for item in flagged
    )

    commitments_html = "".join(
        f"""
        <li>
            {item['text']}
            — Sources:
            {", ".join(item['source_ids'])}
        </li>
        """
        for item in commitments
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>inboxHero Dashboard</title>
</head>

<body>

    <h1>inboxHero Dashboard</h1>

    <section>
        <h2>Pending actions</h2>
        <ul>
            {pending_html}
        </ul>
    </section>

    <section>
        <h2>Flagged</h2>
        <ul>
            {flagged_html}
        </ul>
    </section>

    <section>
        <h2>Commitments</h2>
        <ul>
            {commitments_html}
        </ul>
    </section>

</body>
</html>
"""

    Path("dashboard.html").write_text(
        html,
        encoding="utf-8",
    )

    Path("dashboard.json").write_text(
        json.dumps(
            dashboard_data,
            indent=2,
        ),
        encoding="utf-8",
    )

    log_event({
        "event": "dashboard",
        "cap": "R6",
    })

    print("dashboard.html created")
    print("dashboard.json created")


if __name__ == "__main__":
    generate_dashboard()
