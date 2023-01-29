from typing import Dict
import sys
from traceback import TracebackException
import requests

from .abstracts import RestBase


class UDRest(RestBase):
    url = "http://lindat.mff.cuni.cz/services/udpipe/api"

    def __init__(self) -> None:
        super().__init__()

    def get_models(self):
        pass

    def get_process(self, params: Dict["str", "str"]) -> str:
        try:
            r = requests.get(url=f"{self.url}/process", params=params)
            r.raise_for_status()

        except BaseException as e:
            msg = f"{r.content.decode()}\n\n"
            msg += "\n".join(TracebackException.from_exception(e).format())
            sys.exit(f"{msg}")

        return r.json()["result"]

    @classmethod
    def name(self):
        return self.__name__


if __name__ == "__main__":
    udp_ar = UDRest()
    params = {
        "tokenizer": "",
        "tagger": "",
        "parser": "",
        "model": "arabic",
        "data": "عاد أحمد من المدرسة معها."
    }
    conllu_ar = udp_ar.get_process(params=params)
    print(conllu_ar)
    print(udp_ar.name())
