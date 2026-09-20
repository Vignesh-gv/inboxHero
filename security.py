from rules import is_hostile_message
from trace import log_event


def scan_hostile_messages(messages):
    flagged = []

    for message in messages:
        if is_hostile_message(message):
            item = {
                "message_id": message["id"],
                "attempted_action": message["body"],
                "action_taken": "refused",
            }

            flagged.append(item)

            log_event({
                "event": "refusal",
                "cap": "R5",
                "message_id": message["id"],
                "attempted_action": message["body"],
                "action": "refused",
            })

    return flagged
