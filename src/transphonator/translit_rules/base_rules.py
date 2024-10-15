from abc import ABC, abstractmethod


class BaseTranslitRule(ABC):
    @abstractmethod
    def apply(self, text: str) -> str:
        """Apply the rule to the given text and return the modified text."""
        pass
