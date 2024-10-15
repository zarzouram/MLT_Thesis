from abc import ABC, abstractmethod
from typing import Union


class BaseTransliterator(ABC):
    @abstractmethod
    def transphonate(self, word: str) -> Union[str, None]:
        pass
