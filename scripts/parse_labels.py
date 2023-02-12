# from collections import defaultdict
from typing import List

from pathlib import Path
import json

from utils import parse_arguments
import parsers_m.ud_parsers as Parsers

if __name__ == "__main__":

    # load configuration file:
    #  - Define supported languages and parser
    with open("scripts/config.json", "r") as json_file:
        configs = json.load(json_file)  # type: dict

    # parse arguments
    _, args = parse_arguments()
    wikidata_path = Path(args.wiki_path).absolute().resolve()
    output_dir = Path(args.output_dir).resolve().absolute()
    langs = args.langs  # type: str
    parser_names = args.parsers  # type: str

    # check that the choosed languages and parsers are supported
    parsers_supported = configs['parsers'].keys()
    langs_supported = configs['langs']
    assert all([p in parsers_supported for p in parser_names])
    assert all([ln in langs_supported for ln in langs])

    # - Read json file containing wikidata information.
    # - Parse each line and store the entity id and its labels in the required
    #     languages into a dict.
    #     If a label for a specific language doesn't exist, the label is saved
    #     as None
    wikidata: dict[str, List[str]] = {"idx": [], **{lang: [] for lang in langs}}
    with open(wikidata_path, "r", encoding="utf-8") as f:
        for line in f:
            entity = json.loads(line)  # type: dict
            ent_id = entity["id"]  # type: str
            wikidata["idx"].append(ent_id)
            for lang in langs:
                wlabels: str = entity["labels"].get(lang, None)
                wikidata[lang].append(wlabels)

    # initialize parser classes under 'data.ud_parsers' module using parser
    # names in the configs.
    parsers = []  # list of intialized classes
    parsers_dict = configs["parsers"]  # map parser_name to parser_class_name
    for parser_name in parser_names:
        parsers.append(getattr(Parsers, parsers_dict[parser_name]["class"])())

    # for each language remove records where the labels is None


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
