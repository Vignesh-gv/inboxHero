import json
from pathlib import Path

TRACE_FILE = Path("trace.jsonl")


def log_event(event):
    with TRACE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")
