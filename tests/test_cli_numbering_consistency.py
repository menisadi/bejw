from pathlib import Path

from typer.testing import CliRunner

from bejw.main import app
from bejw.models import Link, ReadingList
from bejw.storage import load, save


runner = CliRunner()


def test_remove_uses_unread_numbering_by_default(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    reading_list = ReadingList(
        capacity=10,
        links=[
            Link(
                id="id-read",
                title="Read First",
                url="https://example.com/read",
                created_at="2024-01-01T00:00:00+00:00",
                read_at="2024-01-10T00:00:00+00:00",
            ),
            Link(
                id="id-unread-1",
                title="Unread One",
                url="https://example.com/unread-1",
                created_at="2024-01-02T00:00:00+00:00",
            ),
            Link(
                id="id-unread-2",
                title="Unread Two",
                url="https://example.com/unread-2",
                created_at="2024-01-03T00:00:00+00:00",
            ),
        ],
    )
    save(reading_list, str(file_path))

    result = runner.invoke(app, ["remove", "1", "--file-path", str(file_path)])

    assert result.exit_code == 0
    updated = load(str(file_path))
    assert [link.id for link in updated.ordered_links()] == ["id-read", "id-unread-2"]


def test_add_confirmation_number_uses_unread_numbering(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"
    reading_list = ReadingList(
        capacity=10,
        links=[
            Link(
                id="id-read",
                title="Read First",
                url="https://example.com/read",
                created_at="2024-01-01T00:00:00+00:00",
                read_at="2024-01-10T00:00:00+00:00",
            ),
            Link(
                id="id-unread-1",
                title="Unread One",
                url="https://example.com/unread-1",
                created_at="2024-01-02T00:00:00+00:00",
            ),
        ],
    )
    save(reading_list, str(file_path))

    result = runner.invoke(
        app,
        [
            "add",
            "https://example.com/new",
            "New Link",
            "--file-path",
            str(file_path),
        ],
    )

    assert result.exit_code == 0
    assert result.stdout == "Added #2\n"
