# from collections import defaultdict
from typing import Dict, List, Type
from scripts.parsers_m.abstracts import AbstractUDParser

from pathlib import Path
import json

from scripts.utils import parse_arguments
from scripts.wiki_data.WikiData import WikiData
from scripts.data_maniplualtion.utils import read_wikidata
import scripts.parsers_m.ud_parsers as Parsers

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

    # initialize parser classes under 'data.ud_parsers' module using parser
    # names in the configs.
    # list of intialized classes
    parsers: List[Type[AbstractUDParser]] = []
    params: List[Dict[str, str]] = []
    parsers_dict = configs["parsers"]  # parsers configs: class_names, params
    for parser_name in parser_names:
        parsers.append(getattr(Parsers, parsers_dict[parser_name]["class"])())
        params.append(parsers_dict[parser_name]["params"])

    # Read and parse wikidata
    wikidata = WikiData(wikidata_path, langs, read_wikidata)
    wkdata_parsed = wikidata.parse_data(parsers[0], params[0], langs)
    print("h")
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
