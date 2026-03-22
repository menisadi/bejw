from pathlib import Path

from typer.testing import CliRunner

from bejw.main import app
from bejw.models import ReadingList
from bejw.storage import load, save

runner = CliRunner()


def _full_list(tmp_path: Path) -> Path:
    """Create a full reading list (capacity=2) with two links."""
    file_path = tmp_path / "links.json"
    rl = ReadingList(capacity=2)
    rl.add_link("https://one.com", "One")
    rl.add_link("https://two.com", "Two")
    save(rl, str(file_path))
    return file_path


def test_add_when_full_replace_first(tmp_path: Path) -> None:
    file_path = _full_list(tmp_path)

    result = runner.invoke(
        app,
        ["add", "https://new.com", "New", "--file-path", str(file_path)],
        input="1\n",
    )

    assert result.exit_code == 0
    assert "Added #" in result.stdout
    updated = load(str(file_path))
    assert len(updated.links) == 2
    urls = {link.url for link in updated.links}
    assert "https://new.com" in urls
    assert "https://one.com" not in urls


def test_add_when_full_replace_cancel(tmp_path: Path) -> None:
    file_path = _full_list(tmp_path)

    result = runner.invoke(
        app,
        ["add", "https://new.com", "New", "--file-path", str(file_path)],
        input="\n",
    )

    assert result.exit_code == 1
    assert "Cancelled" in result.stdout
    updated = load(str(file_path))
    assert len(updated.links) == 2
    urls = {link.url for link in updated.links}
    assert "https://new.com" not in urls


def test_add_when_full_invalid_input(tmp_path: Path) -> None:
    file_path = _full_list(tmp_path)

    result = runner.invoke(
        app,
        ["add", "https://new.com", "New", "--file-path", str(file_path)],
        input="abc\n",
    )

    assert result.exit_code == 1
    assert "Invalid number" in result.stdout
