# ubl2pdf

`ubl2pdf` convertit une facture électronique **UBL / EN16931** en un PDF lisible.

Le projet a été initialement construit à partir d'exports VIZUP conformes au CIUS français Peppol.

## Principe

```text
XML UBL / EN16931
        ↓
      parser
        ↓
 modèle métier Invoice
        ↓
     renderer
        ↓
       PDF
```

Le XML reste la source de vérité. Le PDF est une représentation humaine de son contenu.
