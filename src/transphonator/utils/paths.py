import argparse
import os
from typing import Tuple

CMU_DICT_PATH = "cmudict-0.7b.txt"
FALLBACK_DICT_PATH = "phonenems_en.txt"


def process_args():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=(
            "Transliterator from English based on the English"
            "phonetic representation."
        )
    )

    # Add a mandatory argument for the base directory
    parser.add_argument(
        "data_dir",
        type=str,
        help="The base data absolute directory.",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Get the base directory from the arguments
    data_dir: str = args.data_dir

    # Ensure the base directory is valid
    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid directory")
        exit(1)

    return data_dir


def get_data_dir(base_data_dir: str) -> Tuple[str, str]:
    """Get absolute path of the dictionaries based on a base data directory.

    Args:
        base_data_dir (str): The absolute directory of the data that contains
        the dictionaries.

    Returns:
        Tuple[str, str]: The absolute path of the CMU and fallback
        dictionaries.
    """
    cmu_dict_path = os.path.join(base_data_dir, CMU_DICT_PATH)
    fullback_dict_path = os.path.join(base_data_dir, FALLBACK_DICT_PATH)

    return cmu_dict_path, fullback_dict_path
