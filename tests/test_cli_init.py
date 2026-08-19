from pathlib import Path

from typer.testing import CliRunner

from bejw.main import app
from bejw.models import ReadingList
from bejw.storage import load, save

runner = CliRunner()


def _existing_list(tmp_path: Path) -> Path:
    file_path = tmp_path / "links.json"
    reading_list = ReadingList(capacity=4)
    reading_list.add_link("https://one.com", "One")
    reading_list.add_link("https://two.com", "Two")
    save(reading_list, str(file_path))
    return file_path


def test_init_creates_list_when_file_missing(tmp_path: Path) -> None:
    file_path = tmp_path / "links.json"

    result = runner.invoke(
        app, ["init", "--capacity", "3", "--file-path", str(file_path)]
    )

    assert result.exit_code == 0
    assert "Initialized reading list" in result.stdout
    assert load(str(file_path)).capacity == 3


def test_init_overwrites_existing_when_confirmed(tmp_path: Path) -> None:
    file_path = _existing_list(tmp_path)

    result = runner.invoke(
        app,
        ["init", "--capacity", "7", "--file-path", str(file_path)],
        input="y\n",
    )

    assert result.exit_code == 0
    assert "already holds 2 links (2 unread) with capacity 4" in result.stderr
    reloaded = load(str(file_path))
    assert reloaded.capacity == 7
    assert reloaded.links == []


def test_init_keeps_existing_when_declined(tmp_path: Path) -> None:
    file_path = _existing_list(tmp_path)

    result = runner.invoke(
        app,
        ["init", "--capacity", "7", "--file-path", str(file_path)],
        input="n\n",
    )

    assert result.exit_code == 1
    assert "Cancelled" in result.stdout
    reloaded = load(str(file_path))
    assert reloaded.capacity == 4
    assert len(reloaded.links) == 2


def test_init_force_skips_confirmation(tmp_path: Path) -> None:
    file_path = _existing_list(tmp_path)

    result = runner.invoke(
        app,
        ["init", "--capacity", "7", "--file-path", str(file_path), "--force"],
    )

    assert result.exit_code == 0
    assert "already holds" not in result.stderr
    reloaded = load(str(file_path))
    assert reloaded.capacity == 7
    assert reloaded.links == []
