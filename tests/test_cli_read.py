import webbrowser
from pathlib import Path

from typer.testing import CliRunner

from bejw.main import app
from bejw.models import Link, ReadingList
from bejw.storage import save


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


def test_read_opens_selected_link_and_prints_confirmation(
    tmp_path: Path, monkeypatch
) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)
    opened: list[str] = []

    def _fake_open(url: str, *_args, **_kwargs) -> bool:
        opened.append(url)
        return True

    monkeypatch.setattr(webbrowser, "open", _fake_open)

    result = runner.invoke(app, ["read", "2", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert opened == ["https://example.com/2"]
    assert result.stdout == "Opened #2: https://example.com/2\n"


def test_read_returns_error_when_number_is_missing(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(app, ["read", "99", "--file-path", str(file_path)])

    assert result.exit_code == 1
    assert result.stdout == "No link found with that number.\n"


def test_read_returns_error_for_empty_list(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    save(ReadingList(capacity=10), str(file_path))

    result = runner.invoke(app, ["read", "1", "--file-path", str(file_path)])

    assert result.exit_code == 1
    assert result.stdout == "No link found with that number.\n"


def test_read_uses_unread_numbering_by_default(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "links.json"
    reading_list = ReadingList(
        capacity=10,
        links=[
            Link(
                id="id-1",
                title="Read Example",
                url="https://example.com/read",
                created_at="2024-01-01T00:00:00+00:00",
                read_at="2024-01-03T00:00:00+00:00",
            ),
            Link(
                id="id-2",
                title="Unread Example",
                url="https://example.com/unread",
                created_at="2024-01-02T00:00:00+00:00",
            ),
        ],
    )
    save(reading_list, str(file_path))
    opened: list[str] = []

    def _fake_open(url: str, *_args, **_kwargs) -> bool:
        opened.append(url)
        return True

    monkeypatch.setattr(webbrowser, "open", _fake_open)

    result = runner.invoke(app, ["read", "1", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert opened == ["https://example.com/unread"]
    assert result.stdout == "Opened #1: https://example.com/unread\n"
