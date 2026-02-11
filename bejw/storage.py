from __future__ import annotations

import json
from pathlib import Path

from .models import ReadingList


def load(file_path: str) -> ReadingList:
    """Load the reading list from a JSON file."""
    path = Path(file_path).expanduser()
    if not path.exists():
        return ReadingList()
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReadingList.from_dict(data)


def save(reading_list: ReadingList, file_path: str) -> None:
    path = Path(file_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(reading_list.to_dict(), indent=2)
    path.write_text(payload, encoding="utf-8")
