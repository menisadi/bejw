from pathlib import Path

from typer.testing import CliRunner

from bejw.main import app
from bejw.models import ReadingList
from bejw.storage import load, save

runner = CliRunner()


def _list_file(tmp_path: Path, capacity: int, titles: list[str]) -> Path:
    file_path = tmp_path / "links.json"
    reading_list = ReadingList(capacity=capacity)
    for title in titles:
        reading_list.add_link(f"https://{title.lower()}.com", title)
    save(reading_list, str(file_path))
    return file_path


def test_capacity_raise_refused_when_full(tmp_path: Path) -> None:
    file_path = _list_file(tmp_path, 2, ["One", "Two"])

    result = runner.invoke(app, ["capacity", "5", "--file-path", str(file_path)])

    assert result.exit_code == 1
    assert "Mark something read before raising capacity" in result.stderr
    assert load(str(file_path)).capacity == 2


def test_capacity_raise_allowed_with_headroom(tmp_path: Path) -> None:
    file_path = _list_file(tmp_path, 2, ["One"])

    result = runner.invoke(app, ["capacity", "5", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert "Capacity set to 5" in result.stdout
    assert load(str(file_path)).capacity == 5


def test_capacity_lower_allowed_when_full(tmp_path: Path) -> None:
    file_path = _list_file(tmp_path, 2, ["One", "Two"])

    result = runner.invoke(app, ["capacity", "1", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert load(str(file_path)).capacity == 1


def test_capacity_rejects_zero(tmp_path: Path) -> None:
    file_path = _list_file(tmp_path, 2, [])

    result = runner.invoke(app, ["capacity", "0", "--file-path", str(file_path)])

    assert result.exit_code == 1
    assert "at least 1" in result.stderr
    assert load(str(file_path)).capacity == 2


def test_capacity_show_prints_bare_number_when_never_changed(tmp_path: Path) -> None:
    file_path = _list_file(tmp_path, 3, [])

    result = runner.invoke(app, ["capacity", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert result.stdout.strip() == "3"
    assert result.stderr == ""


def test_capacity_show_reports_last_change_on_stderr(tmp_path: Path) -> None:
    file_path = _list_file(tmp_path, 2, [])
    runner.invoke(app, ["capacity", "6", "--file-path", str(file_path)])

    result = runner.invoke(app, ["capacity", "--file-path", str(file_path)])

    assert result.exit_code == 0
    assert result.stdout.strip() == "6"
    assert "raised from 2" in result.stderr
    assert "just now" in result.stderr
