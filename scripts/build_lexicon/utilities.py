from unicodedata import category
from enum import Enum

import re


def is_nonspace_mark(x: str) -> bool:
    """detect diacritics in a string"""
    return bool(category(x) == "Mn")


def remove_diacritics_ar(text: str) -> str:
    """remove diacritics in a string"""
    return ''.join([t for t in text if not is_nonspace_mark(t)])


class Status(Enum):
    """
    This code defines a custom enumeration called Status, which represents the
    different possible states of a request for parsed Arabic word data.

    The enumeration has seven members, each with a unique integer value:

        - EntryFound (1)
        - EntryNotFound (2)
        - RequestException (3)
        - PluralExist (4)
        - BadTitle (5)
        - UNKOWN (6)
        - NoArabic (7)
"""

    EntryFound = 1
    EntryNotFound = 2
    RequestException = 3
    PluralExist = 4
    BadTitle = 5
    UNKOWN = 6
    NoArabic = 7

    @classmethod
    def add_error(cls, error_name):
        """
        This method takes an error_name argument, which is a string representing
        the name of a new error code to add to the enumeration.
        """

        last_code = len(cls._member_names_)
        names = cls._member_names_
        cls._member_map_
        if error_name not in names:
            cls._member_names_.append(error_name)
            setattr(cls, error_name, last_code + 1)
            cls._member_map_[error_name] = last_code + 1


def is_salem_plural(word: str, word_plural: str) -> str:
    """This function processes the plural form of an Arabic noun and determine
    its type. The function uses regular expressions to identify whether the
    plural form is a regular plural or a broken plural, and returns an
    appropriate response based on the type of plural form.

     Args:
    - word_plural (str): The plural form of the Arabic noun to be processed.

    - word (str): The singular form of the Arabic noun.

    Returns:
    -
    """

    # remove diacritics
    word_nodiac = remove_diacritics_ar(word)

    lc = word_nodiac[-1]  # last charachter in word
    # regeular exp
    salm_femn_regx = re.compile(rf'(ال)?{word_nodiac[:-1]}{lc}?(ات)')
    salm_masc_regx = re.compile(rf'(ال)?{word_nodiac}(ون|ين)')

    # should be broken plural if not salem
    is_salm_femn_plural = bool(salm_femn_regx.fullmatch(word_plural))
    is_salm_masc_plural = bool(salm_masc_regx.fullmatch(word_plural))

    if is_salm_femn_plural or is_salm_masc_plural:
        return True
    else:
        return False
