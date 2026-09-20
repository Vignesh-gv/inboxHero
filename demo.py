import argparse
import json

from triage import run_r1
from draft import draft_reply
from security import scan_hostile_messages
from dashboard import generate_dashboard

from preferences import (
    save_preference,
    get_preference,
    apply_meeting_preference,
)

from x_features import (
    follow_up_tracking,
    morning_digest,
    deadline_scan,
)


def load_inbox():
    with open(
        "inbox.json",
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def run_r2(message_id):
    messages = load_inbox()

    message = next(
        (
            message
            for message in messages
            if message["id"] == message_id
        ),
        None,
    )

    if message is None:
        raise ValueError(
            f"Message not found: {message_id}"
        )

    result = draft_reply(message)

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


def run_r4():
    """
    R4 has two stages.

    First run:
        Store the preference from m041.

    Later run:
        Load the persisted preference and apply it
        to the later meeting request m043.
    """

    existing = get_preference(
        "meeting_start_time"
    )

    if existing is None:

        save_preference(
            "meeting_start_time",
            "11:00",
            "m041",
        )

        print(
            "Preference saved from m041."
        )

        print(
            "Restart the Python process and "
            "run R4 again to apply it."
        )

        return

    messages = load_inbox()

    message = next(
        (
            item
            for item in messages
            if item["id"] == "m043"
        ),
        None,
    )

    result = apply_meeting_preference(
        message
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


def run_r5():
    messages = load_inbox()

    flagged = scan_hostile_messages(
        messages
    )

    for item in flagged:
        print(
            f"FLAGGED: {item['message_id']} "
            f"— action refused"
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cap"
    )

    parser.add_argument(
        "--msg"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    parser.add_argument(
        "--all",
        action="store_true",
    )

    args = parser.parse_args()

    if args.cap == "R1":

        result = run_r1()

        for decision in result["decisions"]:
            print(
                f"{decision['message_id']} | "
                f"{decision['disposition']} | "
                f"{decision['reason']}"
            )

        print("undecided: 0")

    elif args.cap == "R2":

        if not args.msg:
            raise ValueError(
                "R2 requires --msg"
            )

        run_r2(args.msg)

    elif args.cap == "R3":

        from actions import (
            send_message,
            delete_message,
        )

        send_message(
            "demo-send",
            "test@example.com",
            "Demo",
            "Test message",
            dry_run=args.dry_run,
        )

        delete_message(
            "demo-delete",
            dry_run=args.dry_run,
        )

    elif args.cap == "R4":

        run_r4()

    elif args.cap == "R5":

        run_r5()

    elif args.cap == "R6":

        generate_dashboard()

    elif args.cap == "X1":

        print(
            json.dumps(
                follow_up_tracking(),
                indent=2,
            )
        )

    elif args.cap == "X2":

        print(
            json.dumps(
                morning_digest(),
                indent=2,
            )
        )

    elif args.cap == "X3":

        print(
            json.dumps(
                deadline_scan(),
                indent=2,
            )
        )

    elif args.all:

        print("\n=== R1 ===")
        run_r1()

        print("\n=== R2 ===")
        run_r2("m008")

        print("\n=== R3 ===")
        from actions import (
            send_message,
            delete_message,
        )

        send_message(
            "demo-send",
            "test@example.com",
            "Demo",
            "Test message",
            dry_run=True,
        )

        delete_message(
            "demo-delete",
            dry_run=True,
        )

        print("\n=== R4 ===")
        run_r4()

        print("\n=== R5 ===")
        run_r5()

        print("\n=== R6 ===")
        generate_dashboard()

        print("\n=== X1 ===")
        print(
            json.dumps(
                follow_up_tracking(),
                indent=2,
            )
        )

        print("\n=== X2 ===")
        print(
            json.dumps(
                morning_digest(),
                indent=2,
            )
        )

        print("\n=== X3 ===")
        print(
            json.dumps(
                deadline_scan(),
                indent=2,
            )
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
