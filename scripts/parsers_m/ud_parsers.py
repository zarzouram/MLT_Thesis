from typing import Dict, List, Optional, Union

import sys
from traceback import TracebackException

# import re
from tqdm.auto import tqdm

from itertools import chain
import requests
import stanza

from ..parsers_m.interfaces import RestAPIParser, LibraryParser
from ..utils.utils import split_list

TokenDict = Dict[str, Union[str, int]]  # {'id': 1, 'UPON': 'Noun', ...}
SentDict = List[TokenDict]
DoctDict = List[SentDict]


class UDPipeRestParser(RestAPIParser):
    """Concrete class for UDPipe parser REST API.

    This class implements the REST API for UDPipe.
    'https://lindat.mff.cuni.cz/services/udpipe/api-reference.php'
    """

    _url = "http://lindat.mff.cuni.cz/services/udpipe/api"

    def __init__(self, langs: Optional[List[str]], params: Optional[dict]):
        super().__init__()
        # max text length in request = 1000
        self.max_len = 1000
        self.__get_lang_params(langs, params)  # get parameter for each lang

    @property
    def url(self) -> str:
        return self._url

    def __get_lang_params(self, langs: List[str], params: dict):
        # parameters are common for used lang
        self.params = {lang: params for lang in langs}  # type: Dict[str, dict]

    def parse(self, texts: List[str], lang: str) -> str:
        # parsing the text using UDPipe API
        # Split the list of stings to avoide long request error
        chunks = split_list(texts, self.max_len)
        parsed_chuncks = []
        for chunk in tqdm(chunks, desc=f'Parsing {lang}'):
            chunk = "\n\n".join(chunk.split("\n"))
            parsed_chuncks.append(self.__parse(chunk, lang))
        return '\n'.join(parsed_chuncks)

    def __parse(self, text: str, lang: str) -> str:
        # implementation of parsing the text using UDPIPE REST API and
        # returning the UD parse conllu in str format
        params = self.params[lang]
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

    @classmethod
    def name(self):
        return self.__name__


class StanzaParser(LibraryParser):
    """Concrete class for a library-based Universal Dependency Parser.

    This class implements the library-based Universal Dependency Parser and
    inherits from the LibraryParser class. It implements the `parse` and
    `get_model_mapping` methods.
    """

    def __init__(self, langs: Optional[List[str]], params: Optional[dict]):
        super().__init__()
        self.max_len = 2000
        self.__extract_lang_params(langs, params)
        self.nlp = {}
        for lang in langs:
            nlp = stanza.Pipeline(
                lang=lang,
                download_method=None,  # TODO: integrate with params config
                tokenize_no_ssplit=True,
                **self.params[lang])
            self.nlp[lang] = nlp

    def __extract_lang_params(self, langs: str, params: Dict[str, dict]):
        # combine common parameters if any with
        if params.get("common", {}):
            common_params = params["common"]
            params_lang = {}
            for lang in langs:
                params_lang[lang] = {**params[lang], **common_params}

            self.params = params_lang
        else:
            self.params = params

    def parse(self, texts: List[str], lang: str) -> DoctDict:
        # implementation of parsing the text using the Stanza and returning
        # the UD parse tree in list of dict object
        chunks = split_list(texts, self.max_len)
        parsed_chuncks = []
        for chunk in tqdm(chunks, desc=f'Parsing {lang}'):
            chunk = "\n\n".join(chunk.split("\n"))
            parsed_chuncks.append(self.nlp[lang](chunk))

        parsed_chuncks = [pc.to_dict() for pc in parsed_chuncks]
        return list(chain.from_iterable(parsed_chuncks))

    def get_model_mapping(self, lang: str) -> str:
        # implementation of mapping the language code to the corresponding
        # model name for the library
        pass

    @classmethod
    def name(self):
        return self.__name__
