import argparse
from pathlib import Path
from typing import List

import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-idir",
        type=str,
        default="data/interim/proper_nouns",
        help="Directory that have the CSV translations.",
    )

    parser.add_argument(
        "-op",
        type=str,
        default="data/Aarne",
        help="Directory that have the morphodicts folder and WordNetAra.gf",
    )

    parser.add_argument(
        "-ts",
        type=str,
        # default="data/Aarne",
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
    output_path = Path(args.op)  # Path to save the output
    time_stamp = args.ts
    pnts: List[str] = args.pnt  # [Mandatory] Proper noun type "LN, SN, GN"

    # Remove PN from prper nouns type if exist
    if "PN" in pnts:
        pnts.remove("PN")
        print("PN cannot be processed by this script.")

    # Read CSV files
    lst_df_pnt_all = []
    for pnt in pnts:
        csv_name = csv_dir / f"{time_stamp}_{pnt}.csv"
        df_pnt_translations = pd.read_csv(csv_name, index_col=0)
        df_pnt_translations["pnt"] = pnt
        lst_df_pnt_all.append(df_pnt_translations)
    # Combine all translations in on DataFrame
    fd_pnts_translations = pd.concat(lst_df_pnt_all)

    # Construct string format for building functions
    str_pl_n = r'pl = "{1:}"'  # plural form to be converted to LN
    str_sg_n = r'sg = "{1:}"'  # singular form to be converted to LN
    # linearization for nouns to be converted to LN
    str_lin_n_nhum = (
        r"lin '{0:}_N' = mkN nohum (wmkN {{g = {2:} ; "
        + rf"{str_sg_n} ; "
        + rf"{str_pl_n} "
        + r"}}) ;"
    )
    str_lin_n_hum = (
        r"lin '{0:}_N' = mkN hum (wmkN {{"
        + rf"{str_sg_n} ; "
        + rf"{str_pl_n} "
        + r"}}) ;"
    )
    # Other linearizations
    str_lin_ln_sn = r"lin '{0:}_{1:}' = mkLN '{0:}_N' ;"
    str_lin_gn = r"lin '{0:}_PN' = mkPN " + r'"{0:}_N" {1:} hum;'
    # Abstract function
    abs_ara_regex = r"fun '{0:}_{1:}' : {1:} ;"
