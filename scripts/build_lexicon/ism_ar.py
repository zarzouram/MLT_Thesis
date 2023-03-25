from typing import List, Optional


class Ism:
    """This class represents an Arabic noun (ism) and stores information about
    its form, lemma, Universal Parts of Speech (upos), root, gender, and
    plural. It also includes methods for updating the plural and comparing two
    instances of the class, so you can use it as key in a dictionary.

    Parameters

    - form (str): the form of the noun

    - lemma (str): the lemma of the noun

    - upos (str): the Universal Parts of Speech of the noun

    - root (Optional[str]): the root of the noun (default is empty string)

    - gender (Optional[str]): the gender of the noun (default is empty string)

    - plural (Optional[List[str]]): a list of possible plural forms of the noun
      (default is empty list)
      """

    def __init__(self,
                 form: str,
                 lemma: str,
                 upos: str,
                 root: Optional[str] = '',
                 gender: Optional[str] = '',
                 plural: Optional[List[str]] = '') -> None:
        self.form = form
        self.lemma = lemma
        self.upos = upos
        self.root = root
        self.gender = gender
        self.plural = plural

    def update_plural(self, plurals: List[str]):
        """Updates the plural forms of the noun with the given list of plurals.

        Args:
            plurals (List[str]): A list of possible plural forms of the noun.
        """
        # get pluras form that are not is self.plural, then update
        plurals_new = list(set(plurals) - set(self.plural))
        if plurals_new:
            self.plural.extend(plurals_new)

    def __eq__(self, other):
        """Compares two instances of the Ism class for equality based on their
        form and lemma.

        Args:
            other (Ism): The other instance of the Ism class to compare to.

        Returns:
            bool: True if the instances are equal, False otherwise.
        """
        if isinstance(other, Ism):
            if not (other.form == self.form):
                return False

            if not (other.lemma == self.lemma):
                return False

            return True

        else:
            raise TypeError(
                f"Cannot compare objects of type {type(other).__name__} with {type(self).__name__}"  # noqa: E501
            )

    def __hash__(self):
        """Returns a hash value for an instance of the class based on its form
        and lemma. Neede if you will use intences of Ism as a dictionary key.

        Returns:
            int: The hash value for the instance.
        """
        return hash((self.form, self.lemma))

    def __repr__(self) -> str:
        plurals = "-".join(self.plural)
        return f'{self.form}[{self.lemma}][ج]({plurals})'

    def __str__(self) -> str:
        plurals = "-".join(self.plural)
        return f'{self.form}[ج]({plurals})'


class IsmDict(dict):
    """
    This class extends the dict class by adding a custom `__setitem__` method
    that overrides the default behavior of setting an item in the dictionary.

    The original purpose of the `__setitem__` method is to update the
    dictionary by adding the value to dictionary according to the key.

    However, in this implementation, it first checks whether the key already
    exists in the dictionary. The class expects that the key is an instence of
    Ism. If the key is already exists, it updates the existing key by merging
    its plural with the new key's plural and adds the value to the existing
    key's value. If it does not exist, it adds the plural to the dictionary as
    is.
    """

    def __setitem__(self, key: Ism, value: list):
        if not isinstance(key, Ism):
            raise TypeError(
                f"Key must be an instance of Ism, got {type(key).__name__}")

        # Find if key already exists in the dictionary
        existing_key = next((k for k in self if k == key), None)
        if existing_key is not None:
            # If key exists, update its plural and add value to its value
            existing_key.update_plural(key.plural)
            super().__setitem__(existing_key, self[key] + value)
        else:
            # If key does not exist, add key-value pair to dictionary
            super().__setitem__(key, value)
