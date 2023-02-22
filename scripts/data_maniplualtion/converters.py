from typing import Any, Dict, List, Literal, Optional, Union

import re
from data_maniplualtion.abstarcts import ParsersOutputConverter
from data_maniplualtion.utils import replace_wlist


class UDPipeConverters(ParsersOutputConverter):

    def __init__(self):
        super().__init__()

        # matches sentence boundaries in CoNLL-U text data.
        split_sents_regx = r"(?ms)(?<=# newpar\n)(.*?)(?=\n# newpar|\n$)"
        self.__split_sents_regx = re.compile(split_sents_regx)

        # matches the sent_id field in CoNLL-U formatted text data.
        self.__sent_id_regx = re.compile(r"(?<=# sent_id = )\d+")

    def convert(self, data: Any) -> Dict[str, List[Union[int, str]]]:
        pass

    def change_sent_id(self, data: str, idxs: List[str]) -> str:
        """replaces the sent_id field in CoNLL-U text data with the values in
        idxs (Wikidata ids).
        """
        self.__check_integrity(data, idxs)
        conllu_w_wiki_ids = replace_wlist(self.__sent_id_regx, idxs, data)
        return conllu_w_wiki_ids

    def write2desk(self, data: str, file_path: str,
                   mode: Optional[Literal["a", "w"]] = "w") -> None:

        sents = "\n\n".join(self.__split_sents_regx.findall(data))
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(sents)

    def __check_integrity(self, data: str, idxs: str) -> None:
        """verifies that the length of idxs matches the number of sentences in
        the data
        """
        # split sentences
        sents = self.__split_sents_regx.findall(data)
        # get number of sentences
        sent_ids = self.__sent_id_regx.findall(data)

        assert len(sents) == len(idxs)
        assert len(sent_ids) == len(idxs)

    @classmethod
    def name(self):
        return self.__name__
