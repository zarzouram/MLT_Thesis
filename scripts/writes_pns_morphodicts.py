import argparse
import re
from pathlib import Path

import pandas as pd

PNTS_MAP = {"GN": "PN", "SN": "PN", "LN": "LN"}
STR_MORPHO_NAME = "MorphoDict{0:}Ara{1:}.gf"
WORDNET_ENTRY_REGEX = r"(?<=lin ')(.+?)(?=' \=)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-idir",
        type=str,
        default="data/Aarne/proper_nouns",
        help="Directory that have the processed CSV translations.",
    )

    parser.add_argument(
        "-mdir",
        type=str,
        default="data/Aarne/morphodicts",
        help="Directory to the morphodicts",
    )

    parser.add_argument(
        "-wdgfp",
        type=str,
        default="data/Aarne/WordNetAra.gf",
        help="Path to wordNetAra.gf",
    )

    # Get arguments values
    args = parser.parse_args()
    csv_dir = Path(args.idir)  # Path to csv folder
    morpho_dicts_dir = Path(args.mdir)  # Path to morphodicts folder
    wordnet_ar_path: str = args.wdgfp  # Path to WordNetAra.gf

    # Get file paths
    list_csv_paths = csv_dir.glob("*.csv")

    # Read csv
    list_csv = []
    for csv_p in list_csv_paths:
        list_csv.append(pd.read_csv(csv_p, sep="\t"))
    df_csv = pd.concat(list_csv)
    pnts = df_csv["pnt"].unique().tolist()
    pnts = {PNTS_MAP[pnt] for pnt in pnts}
    df_csv["pnt"] = df_csv["pnt"].apply(lambda x: PNTS_MAP[x])

    # Read morphodicts gf
    for pnt in pnts:
        # Open MorphoDict gf
        morpho_path = morpho_dicts_dir / STR_MORPHO_NAME.format(pnt, "")
        with open(morpho_path, mode="r", encoding="utf-8") as fobj:
            morpho_data = fobj.read()
        # Extract lnearization functions from morphodicts
        list_lins = re.findall(r"^lin .+$",
                               morpho_data,
                               flags=re.MULTILINE)
        df_concretes_new = pd.DataFrame({"concretes": list_lins})
        df_concretes_new["lin_domain"] = (df_concretes_new["concretes"].str
                                          .extract(WORDNET_ENTRY_REGEX))

        # Get linearization functions from csv
        df_pnt_csv = df_csv[df_csv["pnt"] == pnt]
        # Concrate Nouns
        df_concrete_n = (df_pnt_csv.copy()[["wordnet_entry", "concrete_n"]]
                         .dropna(subset=["concrete_n"]))  # drop empty rows

        df_concrete_n["lin_domain"] = (df_concrete_n["concrete_n"]
                                       .str.extract(WORDNET_ENTRY_REGEX)
                                       )
        # Group by lin_domain, list all WordNet entry that have the same
        # lin_domain
        df_concrete_n = (df_concrete_n
                         .groupby(by=["lin_domain", "concrete_n"],
                                  as_index=False)
                         .agg({"wordnet_entry": list})
                         )
        # English words from ?
        # Concrate PN "LN, SN, GN"
        df_concrete_pn = (df_pnt_csv.copy()[["wordnet_entry", "concrete_pn"]]
                          .dropna(subset=["concrete_pn"]))  # drop empty rows
        df_concrete_pn["lin_domain"] = (df_concrete_pn["concrete_pn"]
                                        .str.extract(WORDNET_ENTRY_REGEX)
                                        )
        # print(pd.merge(left=df_concrete_n.set_index("lin_domain"),
        #                right=df_concrete_pn.set_index("lin_domain"),
        #                how="outer",
        #                left_index=True,
        #                right_index=True,
        #                validate="one_to_one",
        #                )
        #       )



