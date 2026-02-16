from pathlib import Path
import json

from bejw.models import ReadingList
from bejw.storage import load, save


def test_load_returns_default_when_file_missing(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"

    reading_list = load(str(file_path))

    assert reading_list.capacity == 10
    assert reading_list.links == []


def test_save_then_load_round_trip(tmp_path: Path) -> None:
    file_path = tmp_path / "nested" / "links.json"
    original = ReadingList(capacity=2)
    original.add_link("https://example.com", "Example")

    save(original, str(file_path))
    loaded = load(str(file_path))

    assert loaded.capacity == 2
    assert len(loaded.links) == 1
    assert loaded.links[0].url == "https://example.com"
    assert loaded.links[0].title == "Example"


def test_load_legacy_payload_without_read_at(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    payload = {
        "capacity": 3,
        "links": [
            {
                "id": "id-1",
                "url": "https://example.com",
                "title": "Example",
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ],
    }
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load(str(file_path))

    assert loaded.capacity == 3
    assert len(loaded.links) == 1
    assert loaded.links[0].read_at is None
