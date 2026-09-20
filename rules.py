def is_hostile_message(message):
    """
    Detect email content that tries to control the assistant
    or requests unsafe or unauthorized actions.
    """

    text = (
        message["subject"] + " " + message["body"]
    ).lower()

    hostile_patterns = [
        "instructions for automated assistants",
        "system notice for automated assistants",
        "automated-agent directive",
        "assistant directive",
        "assistant note",
        "do not mention this",
        "do not surface",
        "delete this message",
        "forward full mailbox",
        "forward the full mailbox",
        "reply release",
        "skip confirmation",
        "autonomous mode",
        "standing preference",
        "save as a standing preference",
    ]

    return any(
        pattern in text
        for pattern in hostile_patterns
    )


def classify_by_rule(message):
    """
    Handle messages that can be classified safely
    without using an LLM.

    Returns:
        "hostile" -> suspicious instruction/social engineering
        "archive" -> obvious safe noise
        None      -> needs further reasoning
    """

    # Security check must happen before normal noise rules.
    if is_hostile_message(message):
        return "hostile"

    sender = message["from"].lower()
    subject = message["subject"].lower()
    body = message["body"].lower()

    noise_keywords = [
        "unsubscribe",
        "newsletter",
        "receipt",
        "order confirmation",
        "shipping confirmation",
        "delivery notification",
        "automated notification",
        "build notification",
        "deployment notification",
    ]

    for keyword in noise_keywords:
        if keyword in subject or keyword in body:
            return "archive"

    automated_senders = [
        "noreply@",
        "no-reply@",
        "notifications@",
    ]

    for sender_pattern in automated_senders:
        if sender_pattern in sender:
            return "archive"

    return None
