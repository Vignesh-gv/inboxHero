from pathlib import Path

from trace import log_event


OUTBOX_DIR = Path("outbox")


def send_message(
    message_id,
    recipient,
    subject,
    body,
    dry_run=False,
):
    """
    Sending is an irreversible action.

    It requires either:
    - dry-run mode, or
    - explicit human approval.
    """

    if dry_run:
        log_event({
            "event": "gate",
            "cap": "R3",
            "action": "send",
            "message_id": message_id,
            "recipient": recipient,
            "decision": "dry-run",
        })

        print(
            f"WOULD SEND: "
            f"{message_id} -> {recipient}"
        )

        return False

    answer = input(
        f"Send message {message_id} "
        f"to {recipient}? [y/n]: "
    ).strip().lower()

    approved = answer == "y"

    log_event({
        "event": "gate",
        "cap": "R3",
        "action": "send",
        "message_id": message_id,
        "recipient": recipient,
        "decision": (
            "approved"
            if approved
            else "rejected"
        ),
    })

    if not approved:
        return False

    OUTBOX_DIR.mkdir(
        exist_ok=True
    )

    output_file = (
        OUTBOX_DIR / f"{message_id}.txt"
    )

    output_file.write_text(
        f"To: {recipient}\n"
        f"Subject: {subject}\n\n"
        f"{body}\n",
        encoding="utf-8",
    )

    print(
        f"SENT: {message_id}"
    )

    return True


def delete_message(
    message_id,
    dry_run=False,
):
    """
    Deleting is an irreversible action.

    It requires either:
    - dry-run mode, or
    - explicit human approval.

    The mock inbox is never actually modified.
    """

    if dry_run:
        log_event({
            "event": "gate",
            "cap": "R3",
            "action": "delete",
            "message_id": message_id,
            "decision": "dry-run",
        })

        print(
            f"WOULD DELETE: {message_id}"
        )

        return False

    answer = input(
        f"Delete message {message_id}? [y/n]: "
    ).strip().lower()

    approved = answer == "y"

    log_event({
        "event": "gate",
        "cap": "R3",
        "action": "delete",
        "message_id": message_id,
        "decision": (
            "approved"
            if approved
            else "rejected"
        ),
    })

    if not approved:
        return False

    # We deliberately do not modify inbox.json.
    print(
        f"DELETE APPROVED: {message_id}"
    )

    return True
