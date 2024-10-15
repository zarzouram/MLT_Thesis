"""
Reference:
https://github.com/AMR-KELEG/English-to-arabic-transphonator/tree/master
"""

import re
from typing import List, Union

from transphonator.phoneme.base_retriever import BasePhonemeRetriever


class CMURetriever(BasePhonemeRetriever):
    def __init__(self, cmu_dict_path, fallback_dict_path=None):
        """Initialize the CMURetriever with an optional fallback dictionary.

        Args:
            fallback_dict_path (str, optional): Path to a custom fallback
            dictionary file. If provided, this file will be used to supplement
            the CMU Pronouncing Dictionary for word-to-phoneme mapping.
            Defaults to None.
        """

        self.english_word_to_phoneme = self.load_cmudict(cmu_dict_path)
        self.fallback_dict = self.load_fallback_dict(fallback_dict_path)

    def load_cmudict(self, cmu_dict_path):
        """Load the CMU dictionary"""
        try:
            with open(
                file=cmu_dict_path,
                encoding="ISO-8859-1",
                mode="r",
            ) as file_obj:
                english_word_to_phoneme = {}
                for line in file_obj:
                    if line.startswith(";;;"):
                        continue
                    # Clean up the line and split into word and phonemes
                    word_phonemes = re.sub(r"[0-9]", "", line.strip()).split()
                    # The word is the first part, the phonemes are the rest
                    word = word_phonemes[0].lower()
                    phonemes = word_phonemes[1:]
                    # Populate the dictionary
                    english_word_to_phoneme[word] = phonemes
        except Exception:
            raise

        return english_word_to_phoneme

    def load_fallback_dict(self, fallback_dict_path):
        """Load the fallback dictionary from a user-provided file."""
        fallback_dict = {}
        try:
            with open(fallback_dict_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    word = parts[0].lower()
                    phonemes = parts[1:]
                    fallback_dict[word] = phonemes
        except Exception:
            pass

        return fallback_dict

    def get_phonemes(self, word: str) -> Union[List[str], None]:
        """Retrieve the phonemes for a given word using the CMU Pronouncing
        Dictionary, with an optional fallback to a custom dictionary.

        Args:
            word (str): The word for which to retrieve the phonemes.

        Returns:
            list: A list of phonemes corresponding to the input word.
                  If the word is not found in either the CMU dictionary or the
                  fallback dictionary,
                  None is returned.

        Example:
            ```
            retriever = CMURetriever()
            phonemes = retriever.get_phonemes("example")
            # Returns something like ['IH0', 'G', 'Z', 'AE1', 'M', 'P', 'L']

            phonemes = retriever.get_phonemes("nonexistentword")
            # Returns None if the word is not found
            ```
        """
        word = word.lower()
        phonemes = self.english_word_to_phoneme.get(word)
        if phonemes is None:
            phonemes = self.fallback_dict.get(word)
        return phonemes
