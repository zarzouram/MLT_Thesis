from typing import List
import argparse
import re


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Universal Dependencies (UD) parsing of Wikidata labels")

    parser.add_argument(
        "--wiki_path",
        type=str,
        default=  # noqa: E251
        "./data/NLG-examples/abstract-wikipedia/properties/wikidata_properties.json",  # noqa: E501
        help="Path for the Wikidata dump json file.")

    parser.add_argument(
        "--parsers",
        nargs='+',
        default=["stanza", "udp"],
        # choices=["stanza", "udp"],
        help=  # noqa: E251
        "Parser to be used. Allowed values are 'udp', and 'stanza'. Pass 'udp' to use UDpipe, 'stanza' to use Stanza and pass 'udp stanze' to use both."  # noqa: E501
    )

    parser.add_argument(
        "--langs",
        nargs='+',
        default=["ar", "en"],
        # choices=["ar", "en"],
        help=  # noqa: E251
        "Language(s) to be processed. Allowed values are 'ar', and 'en'. Pass 'ar' to process Arabic labels, 'en' to process English labels and 'en ar' to process both languages."  # noqa: E501
    )

    parser.add_argument("--output_dir",
                        type=str,
                        default="./outputs/conllu",
                        help="Directory to save conllu files.")

    parser.add_argument("--db_dir",
                        type=str,
                        default="./data/database",
                        help="Directory to save conllu files.")

    args = parser.parse_args()

    return parser, args


def split_list(texts: List[str], max_len: int):
    regex_lenmax = re.compile(rf'.{{,{max_len}}}\n', flags=re.S)
    texts_str = "\n".join(texts)
    chunks: List[str] = re.findall(regex_lenmax, texts_str + "\n")
    return chunks
