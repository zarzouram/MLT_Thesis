import sys
from traceback import TracebackException
import requests

from .interfaces import RestAPIParser, LibraryParser


class UDPipeRestParser(RestAPIParser):
    """Concrete class for UDPipe parser REST API.

    This class implements the REST API for UDPipe.
    'https://lindat.mff.cuni.cz/services/udpipe/api-reference.php'
    """

    _url = "http://lindat.mff.cuni.cz/services/udpipe/api"

    def __init__(self):
        super().__init__()

    @property
    def url(self) -> str:
        return self._url

    def parse(self, text: str, lang: str, params) -> str:
        # implementation of parsing the text using REST API and returning the
        # UD parse conllu in str format
        params["data"] = text
        params["model"] = lang
        try:
            r = requests.get(url=f"{self.url}/process", params=params)
            r.raise_for_status()

        except BaseException as e:
            msg = f"{r.content.decode()}\n\n"
            msg += "\n".join(TracebackException.from_exception(e).format())
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

    def parse(self, text: str, lang: str, params):
        # implementation of parsing the text using the library and returning
        # the UD parse tree
        pass

    def get_model_mapping(self, lang: str) -> str:
        # implementation of mapping the language code to the corresponding
        # model name for the library
        pass

    @classmethod
    def name(self):
        return self.__name__


if __name__ == "__main__":
    udp_ar = UDPipeRestParser()
    params = {
        "tokenizer": "",
        "tagger": "",
        "parser": "",
    }

    text = "\n".join(["عاد أحمد من المدرسة معها.", "ذهب محمد إلى هناك."])
    lang = "ar"
    conllu_ar = udp_ar.parse(text, lang, params=params)
    print(conllu_ar)
    print(udp_ar.name())
