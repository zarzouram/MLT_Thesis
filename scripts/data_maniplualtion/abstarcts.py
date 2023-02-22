from typing import Any, Dict, List, Union
from abc import ABC, abstractmethod


class ParsersOutputConverter(ABC):
    """
    This is an abstract class for converting data to a dict. It provides a
    basic framework for converting data, but concrete implementations will be
    required for each parser.
    """

    @abstractmethod
    def convert(self, data: Any) -> Dict[str, List[Union[int, str]]]:
        """
        This method takes the data as input and returns Dict[str, List[str]].
        The dict is representing a table, where the keys represent the column
        names and the values represents the columns values.
        The first column halds the sent_id from the parser.

        :param data: The input data to be converted.
        :return: Dict[str, List[str]].
        """
        pass
