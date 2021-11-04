"""
This module handles the parsing of the command arguments into an instance
of Arguments. This instance intends to provide type hints which we wouldn't
get if he returned the original Namespace object from argparse module.
"""
from typing import Optional, Set

from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class Arguments:
    min_token_length: Optional[int]
    stopwords: Optional[Set[str]]
    use_potter_stemmer: bool


def _positive_int(value_str: str) -> int:
    value = int(value_str)
    if value <= 0:
        raise f"The value provided ({value}) is not a positive integer"

    return value


def _read_stopwords_file(file_path: str) -> Set[str]:
    stopwords = set()
    with open(file_path, encoding="utf-8") as sw_file:
        for word in sw_file:
            word.strip()
            stopwords.add(word)

    return stopwords


default_arguments = {
    "min_token_length": 3,
    "stopwords": _read_stopwords_file("stopwords.txt"),
    "use_potter_stemmer": True
}

arg_parser = ArgumentParser(
    description="Create an index out of a given Amazon Reviews Corpus.",
    argument_default=default_arguments
)
# Minimum Token Length Handling
arg_parser.add_argument(
    "-mtl", "--min-token-len",
    dest="min_token_length",
    type=_positive_int
)
arg_parser.add_argument(
    "-nmtl", "--no-min-token-len",
    dest="min_token_length",
    action="store_const",
    const=None
)
# Stopwords List Handling
arg_parser.add_argument(
    "-sw", "--stopwords",
    dest="stopwords",
    type=_read_stopwords_file
)
arg_parser.add_argument(
    "-nsw", "--no-stopwords",
    dest="stopwords",
    action="store_const",
    const=None
)
# Use of Potter Stemmer Handling
arg_parser.add_argument(
    "-nst", "--no-stemmer",
    dest="use_potter_stemmer",
    action="store_false"
)


def get_arguments():
    global arg_parser

    arg_values = arg_parser.parse_args()
    return Arguments(
        arg_values.min_token_length,
        arg_values.stopwords,
        arg_values.use_potter_stemmer
    )
