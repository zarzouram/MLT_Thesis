# Command-line arguments handling
import argparse

# Handling text
import math
import re

# Various modules
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import sleep, time

# Type annotation
from typing import DefaultDict, Dict, List, Tuple

# Data handling
import pandas as pd

# Translate text
from google.cloud import translate_v2 as translate


def translate_text(
    values: List[str], target_language_code: str, wait: float = 0.1
) -> List[Dict[str, str]]:
    sleep(wait)
    translate_client = translate.Client()
    results = translate_client.translate(
        values, source_language="en", target_language=target_language_code
    )
    return results


def translate_list_text(
    list_text: List[str], target_language_code: str
) -> List[Dict[str, str]]:
    max_chunk_length = 128
    max_chars_per_minute = 6_000_000
    total_chars = 0
    translated_text: List[Dict[str, str]] = []

    start_time = time()

    for i in range(0, len(list_text), max_chunk_length):
        sub_list = list_text[i:i + max_chunk_length]
        sub_list_chars = sum(len(text) for text in sub_list)

        time_to_wait = 0.1
        if total_chars + sub_list_chars > max_chars_per_minute:
            elapsed_time = time() - start_time
            if elapsed_time < 60:
                time_to_wait = math.ceil(60 - elapsed_time) + 0.02
            start_time = time()
            total_chars = 0

        translated_text.extend(
            translate_text(sub_list, target_language_code, time_to_wait)
        )
        total_chars += sub_list_chars

    return translated_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-ip",
        type=str,
        default="data/Aarne/WordNetAra.gf",
        help="Path to WordNetAra.",
    )
    parser.add_argument(
        "-op",
        type=str,
        default="data/interim/proper_nouns",
        help="Directory to save the translated proper nouns in gf-wordnet.",
    )

    parser.add_argument(
        "-pnt",
        nargs="+",
        required=True,
        # default=["LN", "GN", "SN"],
        help="A list of types of proper names.",
    )

    # Get arguments values
    args = parser.parse_args()
    wordnet_ara_path: str = args.ip  # Path to WordNetAra.gf
    output_path = Path(args.op)  # Path to save the output
    pnts: List[str] = args.pnt  # [Mandatory] Proper noun type "LN, SN, GN"

    # define some variables
    time_stamp = datetime.fromtimestamp(time()).strftime("%Y%m%d.%H%M")

    # Construct some regular expression
    nt_regex = "|".join(pnts)  # regex for nouns type eg. LN|SN|GN
    variants_str = r" = variants \{\}"  # the str ` = variants {}`
    # WordNet consists of the "<word>_<optional-number>_<type-identifier>".
    # For example:
    #   "adam_GN" or "addis_ababa_LN" or "albany_1_LN"
    #   Regex for the word part: (?:.+?)(?=_\d_(?:LN|SN|GN)|_(?:LN|GN|SN))
    wordnet_regex = rf"(?:.+?)(?=_\d_(?:{nt_regex})|_(?:{nt_regex}))"
    # Regex for the whole line that contain LN or GN or SN grouped into six
    # groups
    lin_funs_regex = rf"""(lin\ )  # G1. start of linearization function
                          (                     # G.2 WordNet entry group
                            ({wordnet_regex})   # G.3 Word part
                            (_\d\d?)?           # G.4 Identification Number
                            (_(?:{nt_regex}))   # G.5 Noun identifier
                          )
                          (.;*)    # G.6 The rest of linearization function
                          """
    lin_funs_regex = re.compile(lin_funs_regex, flags=re.VERBOSE)

    # open WordNetAra.gf file
    with open(wordnet_ara_path, mode="rt", encoding="utf-8") as file_obj:
        str_wordnet_ara = file_obj.read()

    # Get linearization lines that have PN or SN or GN or PN grouped into 6
    # groups:
    #   1. literal string "lin "
    #   2. <WordNetEntry>: a. <Word> b. <IdentificationNum> c. <NounIdetifier>
    #   3. <TheRestofFunction>
    list_lin_lines: List[Tuple[str, str, str, str, str, str]]
    list_lin_lines = re.findall(lin_funs_regex, str_wordnet_ara)

    # Get:
    #   1. wordnet that have "Variants {}" as linearization, then translate the
    #      words.
    #   2. wordnet that have linearization function, then extract the
    #      translation from the linearization function (string between double
    #      quote)
    # 1. WordeNet with Variants {}
    #    a. map(Noun_Type -> map(English_Word -> WordNet_Entry_List))
    #    b. translate English_Word, then save them in
    #       map(Noun_Type -> map(WordNet_Entry -> Word_Arabic))
    word2entry_incomp: Dict[str, DefaultDict[str, List[str]]]
    word2entry_incomp = {ntype: defaultdict(list) for ntype in pnts}
    # 2. WordNet entries that have lin functions
    #    map(Noun_Type -> map(WordNet_Entry -> Word_Arabic))
    dict_gf_translated: Dict[str, Dict[str, str]]
    dict_gf_translated = {ntype: {} for ntype in pnts}
    for lin_line in list_lin_lines:
        lin, wordnet_entry, word_en, num, ntype, lin_codomain = lin_line
        ntype = ntype.replace("_", "")
        # No lin function ... translate word ito Arabic
        if lin_codomain.startswith(" = variants {} ;"):
            # Prepare word for translation: Split the word on "_" and
            # capitalizr the first letter of each word
            wrds_captlzd = "-".join(w.capitalize() for w in word_en.split("_"))
            word2entry_incomp[ntype][wrds_captlzd].append(wordnet_entry)
        # WordNet entries that have lin function ... get the translation
        else:
            # Search string between double quote in WordNerAra.gf
            word_ara = re.search(r'(?<=").+?(?=")', lin_codomain)
            # Save data
            if word_ara is not None:
                dict_gf_translated[ntype][wordnet_entry] = word_ara.group()

    # translate incomplete, then save in:
    # map(Noun_Type -> map(WordNet_Entry -> Word_Arabic))
    dict_gf_translation: Dict[str, Dict[str, str]]
    dict_gf_translation = {ntype: {} for ntype in word2entry_incomp.keys()}
    for ntype, word2entry_map in word2entry_incomp.items():
        lst_4trans = list(word2entry_map.keys())
        if lst_4trans:
            # translate
            lst_translated = translate_list_text(lst_4trans, "ar")
            # 1. save translated text
            for translation in lst_translated:
                word_eng = translation["input"]
                word_ara = translation["translatedText"]
                list_wordnet_eng_entry = word2entry_incomp[ntype][word_eng]
                for wordnet_eng_entry in list_wordnet_eng_entry:
                    dict_gf_translation[ntype][wordnet_eng_entry] = word_ara

    # Save data to CSV for manual checking
    for ntype in pnts:
        # entry->word_ara
        wordnet_translated = dict_gf_translated[ntype]
        wordnet_translation = dict_gf_translation[ntype]
        if not wordnet_translated and not wordnet_translation:
            continue
        # Convert to pd.DataFram, concat, save to csv
        df_gf_translated = pd.DataFrame(
            wordnet_translated.items(),
            columns=["wordnet_entry", "translation"],
        )
        df_gf_translation = pd.DataFrame(
            wordnet_translation.items(),
            columns=["wordnet_entry", "translation"],
        )
        df_gf_translated["status"] = "translated"
        df_gf_translation["status"] = "google-translated"
        df_gf_translated["phrase"] = ""
        df_gf_translation["phrase"] = ""
        df_wordnet = pd.concat((df_gf_translation, df_gf_translated))
        df_wordnet.to_csv(output_path / f"{time_stamp}_{ntype}.csv")
