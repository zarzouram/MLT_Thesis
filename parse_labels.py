# from collections import defaultdict
from typing import Dict, List, Type
from scripts.parsers_m.abstracts import AbstractUDParser
from scripts.data_maniplualtion.abstarcts import ParsersOutputConverter

from pathlib import Path
import json

from scripts.utils.utils import parse_arguments
from scripts.data_maniplualtion.utils import read_wikidata

from scripts.wiki_data.WikiData import WikiData
import scripts.parsers_m.ud_parsers as Parsers
import scripts.data_maniplualtion.converters as Converters

if __name__ == "__main__":

    # load configuration file:
    #  - Define supported languages and parser
    with open("scripts/config.json", "r") as json_file:
        configs = json.load(json_file)  # type: dict

    # parse arguments
    _, args = parse_arguments()
    wikidata_path = Path(args.wiki_path).absolute().resolve()
    output_dir = Path(args.output_dir).resolve().absolute()
    db_dir = Path(args.db_dir).resolve().absolute()
    langs = args.langs  # type: str
    parser_names = args.parsers  # type: str

    # check that the choosed languages and parsers are supported
    parsers_supported = configs['parsers'].keys()
    langs_supported = configs['langs']
    assert all([p in parsers_supported for p in parser_names])
    assert all([ln in langs_supported for ln in langs])

    # initialize parser and converter classes using parser names in the
    # configs. parser classes used to parse wikidata labels generating POS,
    # XPOS, deprel, lemma, features. converters used to process the output of
    # paresers
    # list of intialized classes
    parsers: List[Type[AbstractUDParser]] = []
    converters: List[Type[ParsersOutputConverter]] = []
    params: List[Dict[str, str]] = []  # parsers' parmeters
    parsers_dict = configs["parsers"]  # parsers configs: class_names, params
    for parser_name in parser_names:
        # class names
        pclass_name = parsers_dict[parser_name]["class"]
        cclass_name = parsers_dict[parser_name]["output_converter"]
        param = parsers_dict[parser_name]["params"]  # parser parameters
        parsers.append(getattr(Parsers, pclass_name)(langs, param))
        converters.append(getattr(Converters, cclass_name)())
        params.append(param)

    # Read and parse wikidata
    wikidata = WikiData(wikidata_path, langs, read_wikidata)
    for settings in zip(parsers, parser_names, converters, params):
        output_dir_ = str(output_dir / settings[1])
        wkdata_parsed = wikidata.parse_data(parser_obj=settings[0],
                                            converter_obj=settings[2],
                                            params=settings[3],
                                            langs=langs,
                                            write_output=(output_dir_, "w"))
