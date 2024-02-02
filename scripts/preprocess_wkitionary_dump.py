import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path
from typing import List

from tqdm import tqdm

from ar_utils import normalize_ar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load Wikitionary Dump File and Reindex It"
    )

    parser.add_argument(
        "-wp",
        type=str,
        default="../data/raw/wikidata/raw-wiktextract-data.json.gz",
        help="Path for the Wiktionary dump json file.",
    )

    parser.add_argument(
        "-op",
        type=str,
        default="../data/processed/wikidata/ar-wiktextract-data.json.gz",
        help="Path To save the reindexed dump file.",
    )

    parser.add_argument(
        "-ap",
        type=str,
        default="../data/processed/wikidata/ar_reindex.json.gz",
        help="Path To save the reindexed dump file.",
    )

    parser.add_argument(
        "-lg",
        nargs="+",
        default=["ar"],
        help="Languages to extract.",
    )

    args = parser.parse_args()

    langs: List[str] = args.lg  # languages to be extracted
    wiki_path = Path(args.wp)  # Path to wiktionary dump file
    wiki_reindexed_path = Path(args.op)  # Path to save reindexed wikitionary
    wiki_reindices_path = Path(args.ap)  # Path to save the new re-indices

    # TODO: What to do with the old files?
    if wiki_reindexed_path.is_file():
        pass
    if wiki_reindices_path.is_file():
        pass

    # Process the data and gather it in a list
    data_to_write = []
    words_reindexed = defaultdict(list)
    indx = 0

    # Load raw wikitionary dump file:
    # - Extract words belong to `langs`
    # - Reindexing `json` object to be keyed with the extracted words
    # - Save the line number for easier acess in future for each word
    #   - Words can be repeated
    with gzip.open(wiki_path, "rt", encoding="utf-8") as wiki_obj:
        for i, line in enumerate(wiki_obj):
            line_obj = json.loads(line)
            if line_obj.get("lang_code", "") in langs and line_obj.get("word"):
                word = line_obj["word"]
                ar_dict = {k: v for k, v in line_obj.items() if k != "word"}
                word = normalize_ar(word)
                words_reindexed[word].append(indx)
                indx += 1

                # Serialize the new dictionary structure and add it to the list
                data_to_write.append(json.dumps({word: ar_dict}))
            if (i % 999) == 0:
                print(f"Reading Line: {i}", end="\r")

    # Write the list to the GZIP file
    with gzip.open(wiki_reindexed_path, "at", encoding="utf-8") as reindx_obj:
        for entry in tqdm(data_to_write, desc="Write Incdexed Files"):
            reindx_obj.write(entry + "\n")

    # Serialize and write the reindex data
    with gzip.open(wiki_reindices_path, "wt", encoding="utf-8") as indexs_obj:
        json_reindex = json.dumps(words_reindexed)
        indexs_obj.write(json_reindex)
