from unicodedata import category


def is_nonspace_mark(x: str) -> bool:
    """detect diacritics in a string"""
    return bool(category(x) == "Mn")


def remove_diacritics_ar(text: str) -> str:
    """remove diacritics in a string"""
    return "".join([t for t in text if not is_nonspace_mark(t)])
