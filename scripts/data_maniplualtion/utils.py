from typing import List, Pattern
import json

import string

import random


def read_wikidata(path: str, langs: List[str]) -> dict[str, List[str]]:
    """Read Wikidata json file and then extract the labels in the required
    language 'langs'

    Args:
    - path (str): Path to wiki json file.
    - langs (List[str]): a list of language code. For example ['en', 'ar']

    Returns:
    - dict[str, List[str]]: A dictionary that holds the extracted data.
    This dict is like a table where the keys are the column's names. The
    first column, `idx` is the wiki entity index, and the other columns
    are the language code. The dict values are indices and the labels in
    the respective language. For example:
    data = {
    'idx': ['P1', 'P2', 'P3', 'P4'],
    'en': ['instance of', 'country', 'capital', 'currency'],
    'ar': ['عملة' ,'عاصمة' ,'دولة' ,'نوع من الأشياء'],
    'ja': ['インスタンス・オブ', None, '首都', '通貨'],
    'es': ['instancia de', 'país', None, 'moneda']
    }
     """

    # - Read json file containing wikidata information.
    # - Parse each line and store the entity id and its labels in the required
    #     languages into a dict.
    #     If a label for a specific language doesn't exist, the label is saved
    #     as None

    data = {"idx": [], **{lang: [] for lang in langs}}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            entity = json.loads(line)  # type: dict
            ent_id = entity["id"]  # type: str
            data["idx"].append(ent_id)
            for lang in langs:
                wlabels: str = entity["labels"].get(lang, None)
                data[lang].append(wlabels)
    return data


def generate_random_str():
    mystr = ""
    ln = random.randint(5, 10)
    tl_max = 0
    for j in range(ln):
        tl = random.randint(4, 15)
        tl_max = max(tl_max, tl)
        for i in range(tl):
            if i < 2 or i >= tl - 2:
                char = random.choice(string.ascii_letters)
                mystr += char
            else:
                char = random.choice(string.ascii_letters)
                char_space = random.choice([" ", char])
                if mystr[-1] == " ":
                    mystr += char
                else:
                    mystr += char_space
        if j != ln - 1:
            mystr += "\n"
    return mystr


def replace_wlist(pattern: Pattern, list_sub: List[str], text: str) -> str:
    """
    Replaces all occurrences of a regular expression pattern in a text string
    with the next string in a list of replacement strings.

    Args:

    - pattern (Pattern): The compiled regular expression pattern to search
        for in the text.

    - list_sub (List[str]): The list of replacement strings to use when
        replacing each match.  text (str): The text string to search and
        modify.

    Returns:

    - str: The modified text string with all occurrences of the pattern
        replaced by the corresponding strings from the list of replacements.

    Raises:

        ValueError: If the number of replacement strings is not equal to the
        number of matches found in the text.

    Example:
        >> pattern = re.compile(r'\d+')
        >> list_sub = ['one', 'two', 'three', 'four', 'five']
        >> text = '1 2 3 4 5'
        >> result = replace_wlist(pattern, list_sub, text)
        >> print(result)  # 'one two three four five'
    """
    counter_obj = lambda: None  # noqa: E731
    counter_obj.i = -1

    def list_repel(_, counter, list_sub):
        """
        Returns the next string in a list of replacement strings and
        increments a counter.

        Args:

        - _ (Any): The match object returned by the regular expression search
        (not used).

        - counter (lambda: None): The counter object to increment.

        - list_sub (List[str]): The list of replacement strings.

        Returns:

        - str: The next string in the list of replacements.
        """

        counter.i += 1
        return list_sub[counter.i]

    text_new = pattern.sub(
        lambda matchobj: list_repel(matchobj, counter_obj, list_sub), text)
    return text_new
