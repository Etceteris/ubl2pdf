"""Point d'entrée Typer."""

import typer

from ubl2pdf import __version__
from ubl2pdf.commands.convert import convert_command

app = typer.Typer(
    name="ubl2pdf",
    help="Conversion de factures électroniques UBL / EN16931 en PDF.",
    no_args_is_help=True,
)

app.command("convert")(convert_command)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True, help="Afficher la version."),
) -> None:
    """Convertisseur UBL / EN16931 vers PDF."""
