from abc import ABC, abstractmethod
from typing import List, Union


class BasePhonemeRetriever(ABC):
    @abstractmethod
    def get_phonemes(self, word: str) -> Union[List[str], None]:
        """Retrieve phonemes for a given word."""
        pass
