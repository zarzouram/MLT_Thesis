from typing import Any, Dict, List, Type, Union

import sys
from traceback import TracebackException

# import re
from tqdm.auto import tqdm

import requests

from data_maniplualtion.abstarcts import ParsersOutputProcessor
from parsers_m.interfaces import RestAPIParser, LibraryParser
from utils.utils import split_list


class UDPipeRestParser(RestAPIParser):
    """Concrete class for UDPipe parser REST API.

    This class implements the REST API for UDPipe.
    'https://lindat.mff.cuni.cz/services/udpipe/api-reference.php'
    """

    _url = "http://lindat.mff.cuni.cz/services/udpipe/api"

    def __init__(self):
        super().__init__()
        # max text length in request = 1000
        self.max_len = 1000

    @property
    def url(self) -> str:
        return self._url

    def parse(self, texts: List[str], lang: str, params) -> str:
        # parsing the text using UDPipe API
        # Split the list of stings to avoide long request error
        chunks = split_list(texts, self.max_len)
        parsed_chuncks = []
        for chunk in tqdm(chunks, desc=f'Parsing {lang}'):
            chunk = "\n\n".join(chunk.split("\n"))
            parsed_chuncks.append(self.__parse(chunk, lang, params))
        return '\n'.join(parsed_chuncks)

    def __parse(self, text: str, lang: str, params) -> str:
        # implementation of parsing the text using UDPIPE REST API and
        # returning the UD parse conllu in str format
        params["data"] = text
        params["model"] = lang
        try:
            r = requests.get(url=f"{self.url}/process",
                             params=params,
                             timeout=60.)
            r.raise_for_status()

        except BaseException as e:
            # msg = f"{r.content.decode()}\n\n"
            msg = "\n".join(TracebackException.from_exception(e).format())
            sys.exit(f"{msg}")

        return r.json()["result"]

    def get_model_mapping(self, lang: str) -> str:
        # implementation of mapping the language code to the corresponding
        # model name for the REST API.
        pass

    def _convert_output(
        self, data: Any, conv_obj: Type[ParsersOutputProcessor]
    ) -> Dict[str, List[Union[int, str]]]:
        pass

    @classmethod
    def name(self):
        return self.__name__


class StanzaParser(LibraryParser):
    """Concrete class for a library-based Universal Dependency Parser.

    This class implements the library-based Universal Dependency Parser and
    inherits from the LibraryParser class. It implements the `parse` and
    `get_model_mapping` methods.
    """

    def parse(self, texts: List[str], lang: str, params):
        # implementation of parsing the text using the library and returning
        # the UD parse tree
        pass

    def get_model_mapping(self, lang: str) -> str:
        # implementation of mapping the language code to the corresponding
        # model name for the library
        pass

    def _convert_output(
        self, data: Any, conv_obj: Type[ParsersOutputProcessor]
    ) -> Dict[str, List[Union[int, str]]]:
        pass

    @classmethod
    def name(self):
        return self.__name__
