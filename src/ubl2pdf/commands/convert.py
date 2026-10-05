"""Commande de conversion."""

from pathlib import Path
from typing import Annotated

import typer

from ubl2pdf.service import convert


def convert_command(
    xml_file: Annotated[Path, typer.Argument(help="Fichier XML UBL / EN16931 à convertir.")],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Chemin du PDF de sortie. Par défaut : même nom que le XML."),
    ] = None,
) -> None:
    """Convertir une facture électronique UBL en PDF lisible."""
    try:
        destination = convert(xml_file, output)
    except (FileNotFoundError, ValueError) as exc:
        typer.secho(f"Erreur : {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(destination)
