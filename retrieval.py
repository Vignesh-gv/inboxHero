import json


def load_inbox():
    with open("inbox.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_thread_messages(thread_id):
    messages = load_inbox()

    thread_messages = [
        message
        for message in messages
        if message["thread_id"] == thread_id
    ]

    thread_messages.sort(
        key=lambda message: message["timestamp"]
    )

    return thread_messages


def get_earlier_messages(message):
    thread_messages = get_thread_messages(
        message["thread_id"]
    )

    return [
        item
        for item in thread_messages
        if item["timestamp"] < message["timestamp"]
    ]
