# Architecture

Le code sépare volontairement les responsabilités :

- `parser.py` : lecture UBL et normalisation ;
- `models.py` : modèle métier Pydantic ;
- `renderer.py` : présentation PDF ;
- `service.py` : orchestration de la conversion ;
- `commands/` : interface CLI Typer.

Cette séparation permet de faire évoluer le rendu PDF sans modifier la logique de lecture UBL, et inversement.
