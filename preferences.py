import json
import re
from pathlib import Path


PREFS_FILE = Path("prefs.json")


def load_preferences():
    if not PREFS_FILE.exists():
        return {}

    return json.loads(
        PREFS_FILE.read_text(
            encoding="utf-8"
        )
    )


def save_preference(
    key,
    value,
    source,
):
    preferences = load_preferences()

    preferences[key] = {
        "value": value,
        "source": source,
    }

    PREFS_FILE.write_text(
        json.dumps(
            preferences,
            indent=2,
        ),
        encoding="utf-8",
    )


def get_preference(key):
    preferences = load_preferences()

    return preferences.get(key)


def apply_meeting_preference(message):
    preference = get_preference(
        "meeting_start_time"
    )

    if not preference:
        return None

    preferred_time = preference["value"]

    match = re.search(
        r"\b(\d{1,2}):(\d{2})\s*(am|pm)\b",
        message["body"],
        re.IGNORECASE,
    )

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    period = match.group(3).lower()

    if period == "pm" and hour != 12:
        hour += 12

    if period == "am" and hour == 12:
        hour = 0

    meeting_minutes = (
        hour * 60 + minute
    )

    preferred_hour, preferred_minute = map(
        int,
        preferred_time.split(":"),
    )

    preferred_minutes = (
        preferred_hour * 60
        + preferred_minute
    )

    if meeting_minutes < preferred_minutes:
        return {
            "message_id": message["id"],
            "preference_source": preference["source"],
            "original_time": match.group(0),
            "action": (
                "Do not accept the proposed meeting time. "
                "Offer 11:00 AM or later."
            ),
        }

    return None
