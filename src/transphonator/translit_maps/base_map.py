from abc import ABC, abstractmethod


class BaseTranslitMap(ABC):
    @abstractmethod
    def get_equivalent(self, phoneme: str) -> str:
        """Retrieve the equivalent character for a given phoneme."""
        pass
