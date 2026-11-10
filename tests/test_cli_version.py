from importlib.metadata import version

from typer.testing import CliRunner

from bejw.main import app

runner = CliRunner()


def test_version_flag_prints_installed_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == version("bejw")
