from typing import List, Dict, Any, Optional, Type
from abc import ABC, abstractmethod

from data_maniplualtion.abstarcts import ParsersOutputConverter


class AbstractUDParser(ABC):
    """Abstract Class for Universal Dependency Parser used in this thesis.

    This class serves as an interface for all Universal Dependency Parser
    classes.
    """

    @abstractmethod
    def parse(self, texts: List[str], lang: str, params: Optional[dict]) -> Any:
        """Parse the given text and return the UD parse tree.

        Args:

        - text (str): The text to parse.
        - lang (str): The language code of the text, e.g. 'ar', 'en', etc.
        - params (dict, optional): Additional parameters for parsing.

        Returns:

        - Any: The output format will vary based on the implementation
        in the concrete class.


        """
        pass

    @abstractmethod
    def get_model_mapping(self, lang: str) -> str:
        """Return the model name for the given language.

        Args:
        lang (str): The language code.

        Returns:
        str: The model name for the given language.
        """
        pass

    @abstractmethod
    def _convert_output(
            self,
            data: Any,
            conv_obj: Type[ParsersOutputConverter]) -> Dict[str, List[str]]:
        """
        Convert the parser output to the dict format using an instance of
        ParsersOutputProcessor

        Arg:
        data (Any): Data to be converted in the parser output format
        conv_obj (ParsersOutputProcessor): an instance of
        ParsersOutputProcessor to convert the parser output to the dict format

        Returns:
        Dict[str, List[str]]: Converted data in a dict
        """
    pass
