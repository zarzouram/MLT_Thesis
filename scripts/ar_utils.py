from unicodedata import normalize

from pyarabic.araby import DIACRITICS, SHADDA, name


def reorder_shadda(ar_string: str) -> str:
    """unicodedata.normalize put shadda before diacritics"""
    list_ar_str = list(ar_string)

    for i in range(len(list_ar_str) - 1):
        char = list_ar_str[i]
        next_char = list_ar_str[i + 1]

        if char == SHADDA and next_char in DIACRITICS:
            list_ar_str[i], list_ar_str[i + 1] = (
                next_char,
                char,
            )  # Swap shadda and diacritic

    return "".join(list_ar_str)


def normalize_ar(ar_vocalized: str, verbose: bool = False) -> str:
    ar_norm = normalize("NFC", ar_vocalized)
    ar_norm = reorder_shadda(ar_norm)
    if verbose:
        print([name(char) for char in ar_norm])
    return ar_norm
