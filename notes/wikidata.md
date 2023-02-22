# Notes on Wikidata

The data structure for Wiki properties will be look like this:

```python
    {
        "id": "P6",
        "datatype": "wikibase-item",
        "labels": {
            "en": "head of government",
            "it": "capo del governo",
            "de": "Leiter der Regierung oder Verwaltung",
            "fr": "chef ou cheffe de l'exécutif",
            "fi": "hallituksen johtaja",
            "hr": "čelnik vlade",
            "sv": "regeringschef",
            "ar": "رئيس الحكومة",
            "bg": "ръководител"
        },
        "description": "head of the executive power of this town, city,
        municipality, state, country, or other governmental body",
        "aliases": {
            "en": [
                "mayor",
                "prime minister",
                "premier",
                "first minister",
                "head of national government",
                "chancellor",
                "governor",
                "government headed by",
                "executive power headed by",
                "president"
            ],
            "hr": [
                "gradonačelnik"
            ],
            "fr": [
                "maire",
                "bourgmestre",
                "président de commune",
                "syndic",
                "président du gouvernement",
                "président du Conseil",
                "Premier ministre",
                "président de la République",
                "syndique",
                "cheffe de l'exécutif",
                "chef·fe de l'exécutif",
                "chef de l'exécutif"
            ],
            "de": [
                "Ministerpräsident",
                "Bürgermeister",
                "Oberbürgermeister",
                "Ratsvorsitzender",
                "Ortsbürgermeister",
                "Regierungschef",
                "Premierminister",
                "Landrat",
                "Regierungspräsident",
                "Gemeindepräsident"
            ],
            "it": [
                "sindaco",
                "primo ministro",
                "cancelliere",
                "premier",
                "presidente"
            ],
            "sv": [
                "premiärminister",
                "borgmästare",
                "ordförande"
            ],
            "bg": [
                "кмет",
                "министър-председател",
                "президент",
                "председател",
                "областен управител"
            ],
            "ar": [
                "رئيس الوزراء",
                "رئيس مجلس الوزراء",
                "الوزير الأول"
            ]
        }
    }

```
