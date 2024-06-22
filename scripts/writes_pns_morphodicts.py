import argparse
import re

# from distutils.dir_util import copy_tree, remove_tree
from pathlib import Path
from typing import Literal

import pandas as pd

PNTS_MAP = {"GN": "PN", "SN": "PN", "LN": "LN"}
STR_MORPHO_NAME = "MorphoDict{0:}Ara{1:}.gf"
WORDNET_ENTRY_REGEX = r"(?<={0:} ')(.+?)(?=' {1:})"


def get_old_abstract_functions():
    # Open MorphoDict gf
    morpho_abs_path = morpho_dicts_dir / STR_MORPHO_NAME.format(pnt, "Abs")
    with open(morpho_abs_path, mode="r", encoding="utf-8") as fobj:
        morpho_data = fobj.read()

    # Extract lnearization functions from morphodicts: Old Functions, the
    # new function will be add to
    list_lins = re.findall(r"^fun .+;$", morpho_data, flags=re.MULTILINE)
    # Put extracted lines in DataFrame, then get entries for those
    # functions
    df_abs_old = pd.DataFrame({"abstract": list_lins})
    df_abs_old["lin_domain"] = df_abs_old["abstract"].str.extract(
        WORDNET_ENTRY_REGEX.format("fun", r"\:")
    )
    df_abs_old.set_index("lin_domain", inplace=True)

    return df_abs_old


def get_new_functions(
        fun_type: Literal["concrete", "abstract"],
        ntype: Literal["n", "pn"]) -> pd.DataFrame:

    # Initialize related fields to process, either concrete or abstract
    fun_ntype = f"{fun_type}_{ntype}"
    rfields = ["wordnet_entry"]  # related fields
    if fun_type == "concrete":
        rfields.append("status")

    # Get related fields data
    df_data = df_pnt_csv.copy()
    df_data = df_data[rfields + [fun_ntype]].dropna(subset=[fun_ntype])

    # Get entries for the concrete/abstracts
    df_data["lin_domain"] = (df_data[fun_ntype].str.extract(
        WORDNET_ENTRY_REGEX.format(
            "lin" if fun_type == "concrete" else "fun",
            r"\=" if fun_type == "concrete" else r"\:"))
        )
    # Group by lin_domain, list all WordNet entry that have the same
    # lin_domain
    df_data = (
        df_data.groupby(by=["lin_domain", fun_ntype], sort=True)
        .agg({field: list for field in rfields})
        .reset_index()
        .rename(columns={fun_ntype: fun_type})
        .set_index("lin_domain")
    )

    # Remove WordNet entries from pd.DataFrame for abstracts. Already exists in
    # concrete nor need to duplicate
    if fun_type == "abstract":
        df_data.drop("wordnet_entry", axis=1, inplace=True)

    return df_data


def get_old_concrete_functions():
    # Open MorphoDict gf
    morpho_path = morpho_dicts_dir / STR_MORPHO_NAME.format(pnt, "")
    with open(morpho_path, mode="r", encoding="utf-8") as fobj:
        morpho_data = fobj.read()

    # Extract lnearization functions from morphodicts: Old Functions, the
    # new function will be add to
    list_lins = re.findall(r"^lin .+$", morpho_data, flags=re.MULTILINE)
    # Put extracted lines in DataFrame, then get entries for those
    # functions
    df_concretes_old = pd.DataFrame({"concrete": list_lins})
    df_concretes_old["lin_domain"] = df_concretes_old["concrete"].str.extract(
        WORDNET_ENTRY_REGEX.format("lin", r"\=")
    )
    df_concretes_old.set_index("lin_domain", inplace=True)

    return df_concretes_old


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

    # Read csv, get content in pd.DataFrame
    list_csv = []
    for csv_p in list_csv_paths:
        list_csv.append(pd.read_csv(csv_p, sep="\t"))
    df_csv = pd.concat(list_csv)

    # Get the proper noun type from the content
    pnts = df_csv["pnt"].unique().tolist()
    pnts = {PNTS_MAP[pnt] for pnt in pnts}
    df_csv["pnt"] = df_csv["pnt"].apply(lambda x: PNTS_MAP[x])

    # Read morphodicts gf
    for pnt in pnts:
        # Get respective data from csv
        df_pnt_csv = df_csv[df_csv["pnt"] == pnt]
        df_pnt_csv.loc[df_pnt_csv["status"].isna()] = "manual"

        # Get concrate Nouns and their WordNet entries
        # GEt old concrete functions
        df_concretes_old = get_old_concrete_functions()
        # Get new functions to be written from csv
        df_concrete_n = get_new_functions("concrete", "n")
        df_concrete_pn = get_new_functions("concrete", "pn")
        df_concretes_new = pd.concat(
            (df_concrete_n, df_concrete_pn),
            join="outer",
            verify_integrity=True,
        )
        # Concat old and new functions
        df_concretes = pd.concat(
            (df_concretes_old, df_concretes_new),
            join="outer",
            sort=True,
            verify_integrity=True,
        )

        # Get abstract functions
        df_abstract_old = get_old_abstract_functions()
        # Get new functions to be written from csv
        df_abstract_n = get_new_functions("abstract", "n")
        df_abstract_pn = get_new_functions("abstract", "pn")
        df_abstract_new = pd.concat(
            (df_abstract_n, df_abstract_pn),
            join="outer",
            verify_integrity=True,
        )
        # Concat old and new functions
        df_abstracts = pd.concat(
            (df_abstract_old, df_abstract_new),
            join="outer",
            sort=True,
            verify_integrity=True,
        )

        df_functions = pd.merge(
            left=df_concretes,
            right=df_abstracts,
            how="outer",
            right_index=True,
            left_index=True,
            validate="one_to_one",
        )

        all_has_abs = df_functions["abstract"].notna().all()
        all_has_lin = df_functions["concrete"].notna().all()
        assert all_has_abs and all_has_lin

        # Sort to have nouns
        entrykeys_sorted = sorted(
            df_functions.index, key=lambda x: x.split("_")[0]
            )
        if pnt == "PN":
            entrykeys_sorted = sorted(
                entrykeys_sorted, key=lambda x: x.split("_")[1]
                )

        entrykeys_sorted = sorted(
            entrykeys_sorted, key=lambda x: len(x.split("_")[-1])
            )
        df_functions = df_functions.reindex(entrykeys_sorted)
        # Write to files
        # copy old directory
        # morpho_dicts_dir_copy = morpho_dicts_dir / "_copy_1"
        # if morpho_dicts_dir_copy.exists():
        #     remove_tree(morpho_dicts_dir_copy)
        # copy_tree(morpho_dicts_dir, str(morpho_dicts_dir_copy))

        # Write Abstarcts
        text = f"abstract MorphoDict{pnt}AraAbs = Cat ** {{" + "\n"
        text += "\n".join(df_functions["abstract"].to_list())
        text += "\n}"
        morpho_abs_path = morpho_dicts_dir / STR_MORPHO_NAME.format(pnt, "Abs")
        with open(morpho_abs_path, mode="w", encoding="utf-8") as fobj:
            fobj.write(text)

        # Write linearization function
        text = f"concrete MorphoDict{pnt}Ara of MorphoDict{pnt}AraAbs ="
        text += r"CatAra ** open ParadigmsAra in {" + "\n"
        text += "\n".join(df_functions["concrete"].to_list())
        text += "\n}"
        morpho_path = morpho_dicts_dir / STR_MORPHO_NAME.format(pnt, "")
        with open(morpho_path, mode="w", encoding="utf-8") as fobj:
            fobj.write(text)

        # Write to WordNetAra.gf
        df_functions.reset_index(inplace=True)
        df_functions = df_functions[
            ~df_functions["lin_domain"].str.endswith("_N")
            ]
        df_functions = (df_functions
                        .explode(["wordnet_entry", "status"])
                        .dropna(subset="wordnet_entry")
                        .drop(labels=["concrete", "abstract"],
                              axis=1)
                        .drop_duplicates(keep="first")
                        )
        df_functions.set_index("wordnet_entry",
                               inplace=True,
                               verify_integrity=True)
        with open(wordnet_ar_path, mode="rt", encoding="utf-8") as fobj:
            lines = fobj.readlines()
        for i, line in enumerate(lines):
            pattern = r"(?:lin )(.+?)(?: = )"
            match = re.match(pattern, line.strip())
            if match is None:
                continue
            wordnet_entry = match.groups()[0]
            try:
                data = df_functions.loc[wordnet_entry]
                translation = data["lin_domain"]
                status = data["status"]
                lines[i] = (f"lin {wordnet_entry} = "
                            f"'{translation}' ; --{status}\n")
            except KeyError:
                pass
        lines = "".join(lines)
        with open(wordnet_ar_path, mode="wt", encoding="utf-8") as fobj:
            fobj.write(lines)
