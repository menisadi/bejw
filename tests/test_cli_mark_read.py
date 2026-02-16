from pathlib import Path

from typer.testing import CliRunner

from bejw.main import app
from bejw.models import Link, ReadingList
from bejw.storage import load, save


runner = CliRunner()


def _seed_reading_list(file_path: Path) -> None:
    reading_list = ReadingList(
        capacity=10,
        links=[
            Link(
                id="id-1",
                title="Example One",
                url="https://example.com/1",
                created_at="2024-01-01T00:00:00+00:00",
            ),
            Link(
                id="id-2",
                title="Example Two",
                url="https://example.com/2",
                created_at="2024-01-02T00:00:00+00:00",
            ),
        ],
    )
    save(reading_list, str(file_path))


def test_mark_read_marks_entry_and_persists(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(app, ["mark-read", "2", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert result.stdout == "Marked #2 as read.\n"
    updated = load(str(file_path))
    assert updated.links[1].read_at is not None


def test_mark_read_returns_error_when_number_is_missing(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(app, ["mark-read", "99", "--file-path", str(file_path)])

    assert result.exit_code == 1
    assert result.stdout == "No link found with that number.\n"
