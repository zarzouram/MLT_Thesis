from typing import Union

from transphonator.phoneme.base_retriever import BasePhonemeRetriever
from transphonator.pipeline.base_transliterator import BaseTransliterator
from transphonator.translit_maps.base_map import BaseTranslitMap
from transphonator.translit_rules.base_rules import BaseTranslitRule


class TranslitPipeline(BaseTransliterator):
    def __init__(
        self,
        phoneme_retriever: BasePhonemeRetriever,
        transliteration_map: BaseTranslitMap,
        transliteration_rules: BaseTranslitRule,
    ):
        self.phoneme_retriever = phoneme_retriever
        self.transliteration_map = transliteration_map
        self.transliteration_rules = transliteration_rules

    def transphonate(self, word: str) -> Union[str, None]:
        """Transphonate a word into the target language."""

        phonemes = self.phoneme_retriever.get_phonemes(word)
        if not phonemes:
            return None

        phonemes_equivelant = [
            self.transliteration_map.get_equivalent(phoneme)
            for phoneme in phonemes
        ]
        phonemes_equivelant = "".join(phonemes_equivelant)

        transliteration = self.transliteration_rules.apply(phonemes_equivelant)

        return transliteration
