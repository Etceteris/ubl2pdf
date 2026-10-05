# Utilisation

## CLI

```bash
uv run ubl2pdf convert facture.xml
```

Le PDF est créé à côté du XML avec le même nom.

Pour choisir la destination :

```bash
uv run ubl2pdf convert facture.xml --output ./pdf/facture.pdf
```

## Numéro de facture

VIZUP attribue son propre identifiant dans `Invoice/cbc:ID`. Le numéro d'origine du fournisseur est recherché dans un `AdditionalDocumentReference` dont la description vaut `Vendor reference`.

La règle d'affichage est :

1. utiliser la référence fournisseur lorsqu'elle existe ;
2. sinon utiliser l'identifiant VIZUP ;
3. conserver l'identifiant VIZUP comme référence secondaire lorsque les deux sont disponibles.
