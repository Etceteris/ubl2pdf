from pathlib import Path

from typer.testing import CliRunner

from ubl2pdf.cli import app

runner = CliRunner()
FIXTURE = Path(__file__).parent / "fixtures" / "6280310.xml"


def test_cli_convert(tmp_path: Path) -> None:
    output = tmp_path / "invoice.pdf"
    result = runner.invoke(app, ["convert", str(FIXTURE), "--output", str(output)])

    assert result.exit_code == 0
    assert output.is_file()
