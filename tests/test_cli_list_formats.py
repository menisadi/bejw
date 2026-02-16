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
                read_at="2024-01-03T00:00:00+00:00",
            ),
        ],
    )
    save(reading_list, str(file_path))


def test_list_tsv_with_header_and_ids(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(
        app,
        ["list", "--file-path", str(file_path), "--show-ids", "--format", "tsv"],
    )

    assert result.exit_code == 0
    assert (
        result.stdout
        == "no\tid\ttitle\turl\n"
        "1\tid-1\tExample One\thttps://example.com/1\n"
    )


def test_list_csv_without_header(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(
        app,
        ["list", "--file-path", str(file_path), "--format", "csv", "--no-header"],
    )

    assert result.exit_code == 0
    assert result.stdout == "1,Example One,https://example.com/1\n"


def test_list_jsonl_with_ids(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(
        app,
        ["list", "--file-path", str(file_path), "--show-ids", "--format", "jsonl"],
    )

    assert result.exit_code == 0
    assert (
        result.stdout
        == '{"number": 1, "title": "Example One", "url": "https://example.com/1", "id": "id-1"}\n'
    )


def test_list_include_read_shows_read_entries(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    _seed_reading_list(file_path)

    result = runner.invoke(
        app,
        [
            "list",
            "--file-path",
            str(file_path),
            "--show-ids",
            "--format",
            "tsv",
            "--include-read",
        ],
    )

    assert result.exit_code == 0
    assert (
        result.stdout
        == "no\tid\ttitle\turl\n"
        "1\tid-1\tExample One\thttps://example.com/1\n"
        "2\tid-2\tExample Two\thttps://example.com/2\n"
    )
