from typing import Any, List
from abc import ABC, abstractmethod


class ParsersOutputConverter(ABC):
    """
    This is an abstract class for converting data to a Conll-U Formate. It
    provides a basic framework for converting data, but concrete
    implementations will be required for each parser.
    """

    @abstractmethod
    def convert(self, data: Any, labels: List[str], idxs: List[str]) -> str:
        """
        This method takes the data as input and returns a string
        text in Conll-U format. It is expected to change the ids to match
        Wikidata ids.

        Args:

        - data: The parsed labels to be converted to Conll-u from parser native
                format.
        - labels: List[str]: Wikidata labels
        - idx: List[str] Wikidata ids for entities labels
        :return: Dict[str, List[str]].
        """
        pass
