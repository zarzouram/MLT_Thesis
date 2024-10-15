"""
Reference:
https://github.com/AMR-KELEG/English-to-arabic-transphonator/tree/master
"""

from transphonator.translit_maps.base_map import BaseTranslitMap


class TranslitMapAra(BaseTranslitMap):
    def __init__(self):
        # Phoneme to Arabic equivalent mapping
        phonemes = [
            'AO0', 'UH0', 'UW0', 'OY0', 'OW0', 'UW1', 'OY1', 'B', 'P', 'NG',
            'F', 'V', 'AA0', 'AE0', 'AH0', 'EH0', 'EH2', 'AY0', 'EY0', 'AW0',
            'IH0', 'T', 'CH', 'G', 'R', 'K', 'L', 'M', 'HH', 'W', 'N', 'Y',
            'PH', 'UX', 'ZH', 'D', 'JH', 'DH', 'ER0', 'ER2', 'Z', 'S', 'SH',
            'IY0', 'IX', 'TH', 'AH1'
            ]

        arabic_equivalent = [
            'ُو', 'ُو', 'ُو', 'ُو', 'ُو', 'ُو', 'وي', 'ب', 'ب', 'غ', 'ف', 'ف',
            'َا', 'َا', 'َا', 'َا', 'َا', 'َي', 'َي', 'َو', 'ِي', 'ت', 'تش',
            'ج', 'ر', 'ك', 'ل', 'م', 'ه', 'و', 'ن', 'ي', 'ف', 'ُو', 'ج', 'د',
            'دج', 'ذ', 'ر', 'ر', 'ز', 'س', 'ش', 'ِي', 'ِي', 'ث', 'أُ'
            ]
        self.transliteration_map = dict(zip(phonemes, arabic_equivalent))

    def _common_prefix(self, s1, s2):
        """
        Calculate the length of the common prefix between two strings.

        Args:
            s1 (str): First string.
            s2 (str): Second string.

        Returns:
            int: Length of the common prefix.
        """
        match_length = 0
        for c1, c2 in zip(s1, s2):
            if c1 == c2:
                match_length += 1
            else:
                break
        return match_length

    def get_equivalent(self, phoneme: str) -> str:
        """
        Find the closest Arabic equivalent for a given ARPAbet phoneme.

        Args:
            phoneme (str): The ARPAbet phoneme to convert.

        Returns:
            str: The corresponding Arabic character(s).
        """
        available_phonemes = sorted(self.transliteration_map.keys())
        matching_prefix_chars = [
            self._common_prefix(phoneme, trans_phoneme)
            for trans_phoneme in available_phonemes
        ]

        # Find the index of the maximum prefix match
        max_idx = max(
            range(len(matching_prefix_chars)),
            key=lambda i: matching_prefix_chars[i],
        )

        return self.transliteration_map[available_phonemes[max_idx]]
