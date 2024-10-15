import re
from typing import List, Union

from transphonator.phoneme.base_retriever import BasePhonemeRetriever


class G2pRetriever(BasePhonemeRetriever):
    def __init__(self):
        """Initialize the G2pRetriever, which uses the `g2p_en` library to
        convert English words into their corresponding ARPAbet phonemes.
        """
        from g2p_en import G2p
        self.g2p = G2p()

    def get_phonemes(self, word: str) -> Union[List[str], None]:
        """Retrieve the phonemes for a given word using the `g2p_en` library.

        Args:
            word (str): The English word for which to retrieve phonemes.

        Returns:
            list: A list of phonemes corresponding to the input word.
                  If the word cannot be converted, an empty list is returned.

        Example:
            ```
            retriever = G2pRetriever()
            phonemes = retriever.get_phonemes("example")
            # Returns something like ['IH0', 'G', 'Z', 'AE1', 'M', 'P', 'L']

            phonemes = retriever.get_phonemes("nonexistentword")
            # Returns an empty list if the word cannot be converted
            ````
        """
        phonemes = self.g2p(word)
        return [p for p in phonemes if re.match(r'[A-Z]+[\d]?', p)]
