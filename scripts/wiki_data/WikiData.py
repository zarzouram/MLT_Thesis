from typing import List, Any, Callable, Dict, Type
from scripts.parsers_m.abstracts import AbstractUDParser


class WikiData:
    """
    Wikidata class: read, parse, manipulate, and save data.
    """

    def __init__(self, path: str, langs: List[str],
                 reader: Callable) -> dict[str, List[str]]:

        # Read data using the passed callable. The reader function must return
        # Dict[str, List[str]] = {"idx": [], **{lang: [] for lang in langs}}
        # This dict is like a table where the keys are the column's names. The
        # first column, `idx` is the wiki entity index, and the other columns
        # are the language code. The dict values are indices and the labels in
        # the respective language.
        self.data: dict[str, List[str]] = reader(path, langs)
        self.langs: str = langs  # list of language codes

    def __filter_none(self, lang: str) -> Dict[str, str]:
        """
        Drop labels that is None in each language of langs
        """
        labels = self.data[lang]
        valid_labels = [label for label in labels if label is not None]
        return valid_labels

    def parse_data(self,
                   parser_obj: Type[AbstractUDParser],
                   params: Dict[str, str],
                   langs: List[str] = None) -> Any:
        """
        Parse wikidata labels for each language in langs.
        """
        data = []
        for lang in langs:
            filtered_data = self.__filter_none(lang)
            parsed_data = parser_obj.parse(filtered_data, lang, params)
            data.append(parsed_data)
        return data
