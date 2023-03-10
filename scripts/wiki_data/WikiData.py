from typing import List, Any, Callable, Dict, Literal, Optional, Tuple, Type
from ..parsers_m.abstracts import AbstractUDParser
from ..data_maniplualtion.abstarcts import ParsersOutputConverter


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
        self.data: dict[str, List[str]] = reader(path, langs)  # wikidata
        self.langs: str = langs  # list of language codes

    def __filter_none(self, lang: str) -> Dict[str, str]:
        """
        Drop labels that is None in each language of langs
        """
        labels = self.data[lang]
        idx = self.data['idx']
        valid_labels = {
            idx[i]: label
            for i, label in enumerate(labels) if label is not None
        }
        return valid_labels

    def parse_data(
            self,
            parser_obj: Type[AbstractUDParser],
            converter_obj: Type[ParsersOutputConverter],
            params: Dict[str, str],
            langs: List[str] = None,
            write_output: Optional[Tuple[str, Literal["w",
                                                      "a"]]] = None) -> Any:
        """
        Parse wikidata labels for each language in langs.
        Takes a parser object, a converter object, and the parser's params then
        returns the parsed data.

        Args:

        - parser_obj: An instance of the AbstractUDParser class.
          Responsible for parsing the wikidata labels.

        - converter_obj: An instance of the ParsersOutputProcessor class.
          Responsible for processing the parsed data in the native parser
          fromat.

        - params: A dictionary of parameters that are used by parser_obj.

        - langs: A list of language codes.

        - write_output: optional tuple of a file path and a mode (either "w" or
          "a") to write the parsed data in the CoNLL-U format to a file

        Returns:

        - Parsed data
        """
        data = {}
        for lang in langs:
            filtered_data = self.__filter_none(lang)  # remove None records
            labels = list(filtered_data.values())
            idxs = list(filtered_data.keys())

            # parse wiki labels using parser_obj, then process its output
            parsed_data = parser_obj.parse(labels, lang)
            conllu_data = converter_obj.convert(parsed_data, labels, idxs)

            # write data to file
            if write_output is not None:
                path = f"{write_output[0]}_{lang}.conllu"
                converter_obj.write2desk(conllu_data, path, write_output[1])
        return data
