import argparse
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import pandas as pd
from queries.get_gender import GN_GENDER_SPARQL_TEMPLATE
from SPARQLWrapper import JSON, POST, SPARQLWrapper

# Construct string format for building functions
STR_PL_N = r'pl = "{0:}"'  # plural form to be converted to LN
STR_SG_N = r'sg = "{0:}"'  # singular form to be converted to LN
# linearization for nouns to be converted to LN
STR_LIN_N_NHUM = (
    r"lin '{0:}_N' = mkN nohum (wmkN {{g = {1:} ; "
    + rf"{STR_SG_N} ; "
    + rf"{STR_PL_N} "
    + r"}}) ;"
)
STR_LIN_N_HUM = (
    r"lin '{0:}_{1:}_N' = mkN hum (wmkN {{"
    + rf"{STR_SG_N} ; "
    + rf"{STR_PL_N} "
    + r"}}) ;"
)
# Other linearizations
STR_LIN_LN_SN = r"lin '{0:}{2:}_{1:}' = mk{1:} '{0:}{2:}_N' ;"
STR_LIN_GN = r"lin '{0:}{2:}_PN' = mkPN " + r'"{0:}_N" {1:} hum;'
# Abstract function
STR_ABS_ARA = r"fun '{0:}_{1:}' : {1:} ;"
# WordNet entry (between single quote)
WORDNET_ENTRY_REGEX = r"(?<=lin ').+?(?=')"


def get_gender_info(
    qids: List[str], query_template: str
) -> Union[None, List[Dict[str, Dict[str, Any]]]]:

    # Convert list of Q-ids to SPARQL VALUES clause
    qid_values = " ".join(f"wd:{qid}" for qid in qids)

    # Replace the placeholder with actual Q-ids
    query = query_template.replace("QIDS_PLACEHOLDER", qid_values)

    # SPARQL endpoint
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    # Set the query and return format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # Use POST method to avoid URI too long error
    sparql.setMethod(POST)

    # Execute the query and return the results
    results = sparql.query().convert()
    if isinstance(results, dict):
        return results["results"]["bindings"]

    return None


def process_wordnet_gf(wordnetgf_path: str) -> pd.DataFrame:

    # Read WordNet.gf as pd.DataFrame
    df_gf = pd.read_csv(wordnetgf_path,
                        engine="python",
                        skiprows=2,
                        skipfooter=1,
                        skip_blank_lines=True,
                        names=["abstract", "comment"],
                        delimiter="\t",
                        )
    # Remove extra spaces and literal string "fun "
    df_gf["abstract"] = df_gf["abstract"].str.replace(
        r" {2,}", " ", regex=True)
    df_gf["abstract"] = df_gf["abstract"].str.replace(r"fun ", "", regex=True)
    # Split to get word entry and sources
    regex_ = r" : \w\w*(?: -> \w+)*? ;(?: -- )?"
    df_gf["wordnet_en_entry"], df_gf["source"] = zip(
        *df_gf["abstract"].str.split(regex_, regex=True)
    )
    df_gf["source"] = df_gf["source"].str.strip()
    return df_gf


def construct_abstracts(data_row: pd.Series) -> Tuple[Union[str, float],
                                                      Union[str, float]]:
    # get wordnet_ar entry
    concrete_n: Union[str, float] = data_row["concrete_n"]
    concrete_pn: str = data_row["concrete_pn"]
    # Initialize Arabic WordNet Entry for Nouns
    abstract_n = np.nan
    if isinstance(concrete_n, str):  # There is a noun linearization
        # Get wordNet entry between single quotes
        wordnet_n_ar_entry = re.search(WORDNET_ENTRY_REGEX, concrete_n)
        # Construct Abstracts for Nouns
        if wordnet_n_ar_entry is not None:
            wordnet_n_ar_entry = wordnet_n_ar_entry.group()
            word_entry, pnt = wordnet_n_ar_entry.rsplit("_", 1)
            abstract_n = STR_ABS_ARA.format(word_entry, pnt)
        else:
            abstract_n = np.nan

    # Get wordNet entry between single quotes
    wordnet_pn_ar_entry = re.search(WORDNET_ENTRY_REGEX, concrete_pn)
    # Construct Abstracts for LN and PN (gn_PN and sn_PN)
    if wordnet_pn_ar_entry is not None:
        wordnet_pn_ar_entry = wordnet_pn_ar_entry.group()
        word_entry, pnt = wordnet_pn_ar_entry.rsplit("_", 1)
        abstract_pn = STR_ABS_ARA.format(word_entry, pnt)
    else:
        abstract_pn = np.nan

    return abstract_n, abstract_pn


def construct_concrete_pnoun(data_row: pd.Series) -> str:
    word_ar = data_row["translation"]
    g_masc = data_row["masc"]
    pnt = data_row["pnt"]  # LN, GN, SN, PN

    # Proper Nouns Type modified, either LN or PN
    pnt_mod = pnt if pnt == "LN" else "PN"
    # Word suffix add to word, to prevent duplications between Wordnet entries
    # of LN, GN, PN. 'آرثر_sn_PN' is different from 'آرثر_gn_PN'
    word_suffix = "" if pnt == "LN" else f"_{pnt.lower()}"

    # Construct Linearizations
    if pnt == "LN" or pnt == "SN":
        str_lin = STR_LIN_LN_SN.format(word_ar, pnt_mod, word_suffix)
    elif pnt == "GN":
        gender_suffix = "m" if g_masc == 1 else "f"
        word_suffix = word_suffix + gender_suffix
        str_lin = STR_LIN_GN.format(word_ar,
                                    "masc" if g_masc == 1 else "fem",
                                    word_suffix)
    else:
        raise NotImplementedError

    return str_lin


def construct_concrete_noun(data_row: pd.Series) -> Union[str, float]:
    word_ar = data_row["translation"]
    g_masc = data_row["masc"]   # 1 or NaN
    pnt = data_row["pnt"]  # LN, GN, SN, PN

    if pnt == "SN":
        str_lin = STR_LIN_N_HUM.format(word_ar, pnt.lower())
    elif pnt == "LN":
        str_lin = STR_LIN_N_NHUM.format(word_ar,
                                        "masc" if g_masc == 1 else "fem")
    elif pnt == "GN":
        str_lin = np.nan
    else:
        raise NotImplementedError  # PN

    return str_lin


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-idir",
        type=str,
        default="data/interim/proper_nouns",
        help="Directory that have the CSV translations.",
    )

    parser.add_argument(
        "-gfp",
        type=str,
        default="data/Aarne/WordNet.gf",
        help="Directory that have the CSV translations.",
    )

    parser.add_argument(
        "-op",
        type=str,
        default="data/Aarne/proper_nouns",
        help="Directory to write the results in.",
    )

    parser.add_argument(
        "-ts",
        type=str,
        help="Time stamp for the CVS files to be read",
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
    csv_dir = Path(args.idir)  # Path to csv translations
    wordnet_gf_path: str = args.gfp  # Path to WordNet.gf
    output_dir = Path(args.op)  # Path to save the output
    time_stamp: str = args.ts
    pnts: List[str] = args.pnt  # [Mandatory] Proper noun type "LN, SN, GN"

    # Remove PN from proper nouns type if exist  -- for now
    if "PN" in pnts:
        pnts.remove("PN")
        print("PN cannot be processed by this script.")

    # Read CSV files
    lst_df_pnt_all = []
    for pnt in pnts:
        csv_name = csv_dir / f"{time_stamp}_{pnt}.csv"
        df_translations = pd.read_csv(csv_name, index_col=0)
        # Add Proper Names Type, LN, HN, SN, PN
        df_translations["pnt"] = pnt

        # Get genders for given names from WordNet.gf
        if pnt == "GN":
            # Read WordNet.gf to get Qids for GN
            df_wordnet_gf = process_wordnet_gf(wordnet_gf_path)
            qids = (df_wordnet_gf[df_wordnet_gf["wordnet_en_entry"].str
                    .endswith("_GN")]["source"]
                    .to_list()
                    )
            # query gender
            query_results = get_gender_info(qids, GN_GENDER_SPARQL_TEMPLATE)
            if query_results is None:
                continue
            # save query results in pd.DataFrame
            df_results = []
            for result in query_results:
                given_name_uri = result["givenName"]["value"]
                given_name_qid = given_name_uri.split('/')[-1]
                gender_label = result.get("genderLabel", "masc")
                if not isinstance(gender_label, str):
                    gender_label = gender_label["value"]
                gender_label = 1 if gender_label in {"masc", "uni"} else np.nan
                # has_male_and_female = result["hasMaleAndFemale"]["value"]
                df_results.append({
                    "source": given_name_qid,
                    "masc": gender_label,
                    # "male_and_female": has_both_male_and_female,
                })

            df_results = pd.DataFrame(df_results)
            # update GN's pd.DataFrame with Gender Data
            # Add wordnet entry to query results pd.DataFrame
            df_results = df_results.merge(
                right=(df_wordnet_gf[["wordnet_en_entry", "source"]]
                       .set_index("source")),
                how="left",
                on="source",
                validate="one_to_many"
                )
            # Add gender (masc=1) to GN's pd.DataFram based on entry
            df_translations = df_translations.merge(
                right=(df_results
                       .set_index("wordnet_en_entry")
                       .drop("source", axis=1)),
                how="left",
                left_on="wordnet_entry",
                right_index=True,
                validate="one_to_one",
            )

        # Save pd.DataFrame
        lst_df_pnt_all.append(df_translations)

    # Combine all translations in on DataFrame
    df_translations = pd.concat(lst_df_pnt_all)
    # update phrase if multi-word ans masc
    df_translations["phrase"] = df_translations["translation"].apply(
        lambda x: int(bool(len(x.split()) > 1)))

    # Construct Concrete and abstract functions
    df_translations["concrete_n"] = (
        df_translations[["translation", "masc", "pnt"]].apply(
            construct_concrete_noun, axis=1
            )
        )
    df_translations["concrete_pn"] = (
        df_translations[["translation", "masc", "pnt"]].apply(
            construct_concrete_pnoun, axis=1
            )
        )
    df_translations["abstract_n"], df_translations["abstract_pn"] = zip(
        *df_translations[["concrete_n", "concrete_pn"]].apply(
            construct_abstracts, axis=1,
            )
        )

    # Save to CSV files
    for pnt in df_translations["pnt"].to_list():
        pnt: str
        df_translations_pnt = df_translations.copy()[
            df_translations["pnt"] == pnt]
        df_translations_pnt.set_index("wordnet_entry",
                                      inplace=True,
                                      verify_integrity=True)

        # save to csv
        csv_path = output_dir / f"{pnt}.csv"
        df_translations_pnt.to_csv(csv_path, sep="\t")
