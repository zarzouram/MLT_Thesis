from pathlib import Path
import json

from data.utils import parse_arguments
import data.ud_parsers as Parsers

if __name__ == "__main__":

    with open("scripts/config.json", "r") as json_file:
        configs = json.load(json_file)
    wikiconfigs = configs["wikidata"]

    # parse arguments
    _, args = parse_arguments(wikiconfigs)
    wikidata_path = Path(args.wiki_path).absolute().resolve()
    output_dir = Path(args.output_dir).resolve().absolute()
    langs = args.langs  # type: str
    parser_names = args.parsers  # type: str

    # open Wikidata json file. Get labels for the respective language and
    # the entity ID.
    wikidata = []
    with open(wikidata_path, "r", encoding="utf-8") as f:
        for line in f:
            entity = json.loads(line)  # type: dict
            ent_id = entity["id"]  # type: str
            ent_labels = [(lang, entity["labels"].get(lang, None))
                          for lang in langs]
            wikidata.append((ent_id, ent_labels))

    # initialize parser classes under 'data.ud_parsers' module using parser
    # names
    parsers = []  # list of intialized classes
    parsers_dict =  wikiconfigs["parsers"]  # parser_name to parser_class_name
    for parser_name in parser_names:
        parsers.append(getattr(Parsers, parsers_dict[parser_name])())

"""
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
    municipality, state, country, or other governmental body",  # noqa: E501
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
"""
