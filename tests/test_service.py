from pathlib import Path

from ubl2pdf.service import convert

FIXTURE = Path(__file__).parent / "fixtures" / "6280310.xml"


def test_convert_generates_pdf(tmp_path: Path) -> None:
    output = tmp_path / "invoice.pdf"

    result = convert(FIXTURE, output)

    assert result == output.resolve()
    assert result.is_file()
    assert result.read_bytes().startswith(b"%PDF")
