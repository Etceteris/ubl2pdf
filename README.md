# ubl2pdf

Conversion de factures électroniques **UBL / EN16931** en PDF lisible.

Le projet est conçu à partir d'exports VIZUP conformes au CIUS français Peppol, tout en gardant le parseur indépendant de VIZUP.

## Fonctionnalités

- lecture d'un XML UBL / EN16931 ;
- extraction fournisseur / client ;
- gestion des lignes de facture ;
- gestion de plusieurs sous-totaux de TVA ;
- montants HT, TVA, TTC et net à payer ;
- mentions et conditions portées par le XML ;
- détection de la référence d'origine fournisseur ;
- conservation de l'identifiant VIZUP comme référence secondaire ;
- génération PDF A4 ;
- CLI Typer ;
- tests pytest ;
- documentation MkDocs Material.

## Règle du numéro de facture

Dans les XML VIZUP étudiés, `Invoice/cbc:ID` correspond à un identifiant attribué par VIZUP. La référence d'origine du fournisseur est portée par :

```xml
<cac:AdditionalDocumentReference>
    <cbc:ID>EGCFRD0014640073</cbc:ID>
    <cbc:DocumentDescription>Vendor reference</cbc:DocumentDescription>
</cac:AdditionalDocumentReference>
```

Le PDF affiche donc :

1. `Vendor reference` comme numéro principal lorsqu'elle existe ;
2. `cbc:ID` comme référence VIZUP ;
3. `cbc:ID` comme numéro principal si aucune référence fournisseur n'est disponible.

## Structure

```text
ubl2pdf/
├── .python-version
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── docs/
│   ├── guide/
│   ├── reference/
│   └── index.md
├── src/
│   └── ubl2pdf/
│       ├── commands/
│       │   └── convert.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── constants.py
│       ├── fonts.py
│       ├── models.py
│       ├── parser.py
│       ├── renderer.py
│       └── service.py
├── tests/
│   ├── fixtures/
│   │   └── 6280310.xml
│   ├── test_cli.py
│   ├── test_parser.py
│   └── test_service.py
├── .gitignore
├── mkdocs.yml
├── pyproject.toml
└── README.md
```

## Installation

Le projet cible Python 3.14 et utilise `uv`.

```bash
uv python install 3.14.5
uv venv .venv
uv sync
```

Pour installer également les outils de développement :

```bash
uv sync --group dev
```

Pour la documentation :

```bash
uv sync --group docs
```

## Utilisation

```bash
uv run ubl2pdf convert facture.xml
```

Par défaut, `facture.pdf` est créé à côté de `facture.xml`.

Destination explicite :

```bash
uv run ubl2pdf convert facture.xml --output ./pdf/facture.pdf
```

Le module Python est également exécutable :

```bash
uv run python -m ubl2pdf convert facture.xml
```

## Qualité et tests

```bash
uv run --group dev pytest
uv run --group dev pytest --cov=ubl2pdf
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev bandit -c pyproject.toml -r src
```

## Documentation

```bash
uv run --group docs mkdocs serve
```

Build statique :

```bash
uv run --group docs mkdocs build --strict
```

## Principe d'architecture

```text
XML UBL / EN16931
        │
        ▼
      parser
        │
        ▼
  modèle Pydantic
        │
        ▼
     renderer
        │
        ▼
       PDF
```

Le XML reste la source de vérité. Le PDF est uniquement une représentation lisible des données qu'il contient.
