import argparse
import re
from datetime import datetime
from pathlib import Path
from time import sleep, time
from typing import List

import pandas as pd
from google.cloud import translate_v2 as translate
from tqdm import tqdm


def translate_text(values: str, target_language_code: str):
    sleep(1.0)
    translate_client = translate.Client()
    result = translate_client.translate(values, source_language="en", target_language=target_language_code)
    return result["input"], result["translatedText"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape gf-wordnet from a .")

    parser.add_argument(
        "-op",
        type=str,
        default="data/interim/gf_wordnet",
        help="Directory to save the parsed gf-wordnet.",
    )

    parser.add_argument(
        "-qids",
        nargs="+",
        # default=["Q79", "Q34", "Q16"],
        help="A list if Wikidata entities' ID.",
    )

    # Get arguments values
    args = parser.parse_args()
    qids: List[str] = args.qids  # languages to be extracted
    output_path = Path(args.op)  # Path to save reindexed wikitionary

    # define some variables
    TIME_STAMP = date_time = datetime.fromtimestamp(time()).strftime("%Y%m%d.%H%M")
    # Path to wikimin gf functions
    wikimin_path = Path("data/external/wikimini/data/all_trees.txt")
    # Regex to extract entity related gf-functions
    str_entity_pattern = r"(^-- {}\n)(.+?)(^-- Q\d+$|\n$)"

    # open wikimini text file
    # with open(wikimin_path, mode="r", encoding="utf-8") as file_obj:
    #     str_wikimini = file_obj.read()
    with open(wikimin_path, mode="r", encoding="unicode_escape") as file_obj:
        str_wikimini = file_obj.read()

    # Encode text file to handel unicode escape
    str_wikimini = str_wikimini.encode("latin1").decode("utf-8")

    # Extract gf-wordnet from Wikimini
    print(f"Get data for {' '.join(qids)}")
    str_entities = [
        match.groups()[1]
        for qid in qids
        for match in [
            re.search(
                str_entity_pattern.format(qid),
                str_wikimini,
                flags=re.DOTALL | re.MULTILINE,
            )
        ]
        if match
    ]
    # Extract gf-wordnet
    gf_wordnet = set(re.findall(r"(?:[\w-]+_)+[\d_]{0,2}[a-zA-Z]{1,2}\b", "\n".join(str_entities)))

    # Load previous gf-wordnet
    prev_gf_wordnet_en = set()
    gf_wordnet_paths = list(output_path.glob("*ar2en_words_gf.csv"))
    for path in gf_wordnet_paths:
        prev_gf_wordnet = set(pd.read_csv(path, index_col=0, delimiter="\t")["en_entry"].to_list())
        prev_gf_wordnet_en.update(prev_gf_wordnet)

    # Get non-processed gf-wordnet
    gf_wordnet = sorted(gf_wordnet.difference(prev_gf_wordnet_en))

    if gf_wordnet:
        # Get the English Translation
        dict_gf_wordnet_en_ar = {"en_entry": [], "en": [], "ar": [], "pos": []}
        pos_pattern = re.compile(r"(?<=_)\w{1,2}$")
        for gf_word_entry_en in tqdm(gf_wordnet):
            # POS is the Last element when split by "_"
            *list_gf_word, pos = gf_word_entry_en.split("_")
            # If the last element before the POS is a number omit it from word_en
            word_en = " ".join(list_gf_word)
            if list_gf_word[-1].isdecimal():
                word_en = " ".join(list_gf_word[:-1])
            # Translation should be reviwed. For example verbs are translated to present. We want it in past.
            _, word_ar = translate_text(word_en, "ar")
            # Change the POS of Multi Words Nouns and Verbs translation
            if len(word_ar.split()) > 1:
                if pos == "N":
                    pos = "CN"
                elif pos.startswith("V"):
                    pos = "VP"
                for word in word_ar.split():
                    dict_gf_wordnet_en_ar["ar"].append(word)
                    dict_gf_wordnet_en_ar["en"].append("")
                    dict_gf_wordnet_en_ar["en_entry"].append(gf_word_entry_en)
                    dict_gf_wordnet_en_ar["pos"].append("")

            # save data
            dict_gf_wordnet_en_ar["ar"].append(word_ar)
            dict_gf_wordnet_en_ar["en"].append(word_en)
            dict_gf_wordnet_en_ar["en_entry"].append(gf_word_entry_en)
            dict_gf_wordnet_en_ar["pos"].append(pos)

        df_gf_wordnet_en_ar = pd.DataFrame(dict_gf_wordnet_en_ar).sort_values(["en_entry", "pos"])
        filename = f"{'_'.join(qids)}_ar2en_words_gf"
        df_gf_wordnet_en_ar.to_csv(output_path / f"{TIME_STAMP}_{filename}.csv", sep="\t")
