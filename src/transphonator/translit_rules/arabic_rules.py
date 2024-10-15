"""
Reference:
https://github.com/AMR-KELEG/English-to-arabic-transphonator/tree/master
"""

import re

from transphonator.translit_rules.base_rules import BaseTranslitRule


class TranslitRuleAra(BaseTranslitRule):
    def __init__(self):
        # Mapping of short vowels to long vowels
        self.short_to_long_vowel_dict = {
            "\u064E": "و",  # Fatha to Waw
            "\u064F": "ا",  # Damma to Alef
            "\u0650": "ي",  # Kasra to Ya
        }

        # Arabic character sets
        self.arabic_consonants = ["ب", "ت", "ث", "ج", "ح", "د", "ذ", "ر", "ز",
                                  "س", "ش", "غ", "ف", "ق", "ك", "ل", "م", "ن",
                                  "ه"]

        self.arabic_vowels = ["ا", "أ", "و", "ي", "ى"]
        # Fatha, Damma, Kasra (short vowels)
        self.arabic_short_vowels = ["\u064E", "\u064F", "\u0650"]

    def apply(self, text: str) -> str:
        """Apply transliteration rules to adjust the Arabic text.

        Args:
            text (str): The initial Arabic transliteration.

        Returns:
            str: The adjusted Arabic transliteration.
        """
        arabic_vowels_str = re.escape("".join(self.arabic_vowels))
        arabic_consonants_str = re.escape("".join(self.arabic_consonants))
        arabic_short_vowels_str = re.escape("".join(self.arabic_short_vowels))

        # Rule 1: Handle starting Fatha
        text = re.sub("^[\u064E\u064F]", "أ", text)
        text = re.sub("^[\u0650]", "إ", text)

        # Rule 2: Replace short vowels at the end
        text = re.sub(
            r"[\u064E\u064F\u0650]$",
            lambda m: self.short_to_long_vowel_dict[m.group()],
            text,
        )

        # Rule 3: Convert short vowels following consonants to long vowels
        groups = re.search(
            f"^([{arabic_vowels_str}][{arabic_consonants_str}])([{arabic_short_vowels_str}])",
            text,
        )
        if groups:
            text = (
                groups.group(1)
                + self.short_to_long_vowel_dict[groups.group(2)]
                + text[3:]
            )

        # Rule 4: Handle 'ng' sound at the end
        text = re.sub(r"نق$", "نغ", text)

        # Rule 5: Handle 'ng' sound in the middle
        text = re.sub(r"نق(?=[{0}])".format(arabic_consonants_str), "ن", text)

        return text
