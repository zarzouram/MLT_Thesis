from abc import abstractmethod
from scripts.parsers_m.abstracts import AbstractUDParser


class RestAPIParser(AbstractUDParser):
    """
    This is an interface class for UD parsers that have REST API based.
    """

    @property
    @abstractmethod
    def url(self) -> str:
        """
        Return the URL of the REST API for the UD parser.
        """
        return self._url


class LibraryParser(AbstractUDParser):
    """
    This is an interface class for library-based UD parsers.
    """
    pass
