# %%
from abc import ABC


class RestBase(ABC):

    @property
    def url(self) -> str:
        return self._url
