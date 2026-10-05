# Installation

## Environnement

Le projet cible Python 3.14 et utilise `uv`.

```bash
uv python install 3.14.5
uv venv .venv
uv sync
```

Dépendances de développement :

```bash
uv sync --group dev
```

Documentation :

```bash
uv sync --group docs
```
