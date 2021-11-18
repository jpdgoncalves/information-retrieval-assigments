"""
This module handles the parsing of the command arguments into an instance
of Arguments. This instance intends to provide type hints which we wouldn't
get if we returned the original Namespace object from argparse module.
"""
from typing import Optional, Set

from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class Arguments:
    corpus_path: str
    min_token_length: Optional[int]
    stopwords: Optional[Set[str]]
    use_potter_stemmer: bool
    memory_threshold: float
    index_path: str


def _positive_int(value_str: str) -> int:
    value = int(value_str)
    if value <= 0:
        raise f"The value provided ({value}) is not a positive integer"

    return value


def _float_between_zero_and_one(value_str: str) -> float:
    value = float(value_str)
    if value < 0.0 or value > 1.0:
        raise f"The value provided ({value}) is not a float between 0.0 and 1.0"

    return value


def _read_stopwords_file(file_path: str) -> Set[str]:
    stopwords = set()
    with open(file_path, encoding="utf-8") as sw_file:
        for word in sw_file:
            stopwords.add(word.strip())

    return stopwords


default_arguments = {
    "min_token_length": 3,
    "stopwords": _read_stopwords_file("stopwords.txt"),
    "use_potter_stemmer": True,
    "memory_threshold": 0.5,
    "index_path": "index.txt"
}

arg_parser = ArgumentParser(
    description="Create an index out of a given Amazon Reviews Corpus."
)
# Minimum Token Length Handling
arg_parser.add_argument(
    "-mtl", "--min-token-len",
    dest="min_token_length",
    type=_positive_int,
    default=default_arguments["min_token_length"]
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
    type=_read_stopwords_file,
    default=default_arguments["stopwords"]
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

# Memory Threshold
arg_parser.add_argument(
    "-memt", "--memory--threshold",
    dest="memory_threshold",
    type=_float_between_zero_and_one,
    default=default_arguments["memory_threshold"]
)

# Handling index path
arg_parser.add_argument(
    "-o", "--index-path",
    dest="index_path",
    default=default_arguments["index_path"]
)

# Handling corpus path
arg_parser.add_argument(
    "corpus_path"
)


def get_arguments():
    global arg_parser

    arg_values = arg_parser.parse_args()

    return Arguments(
        arg_values.corpus_path,
        arg_values.min_token_length,
        arg_values.stopwords,
        arg_values.use_potter_stemmer,
        arg_values.memory_threshold,
        arg_values.index_path
    )


def print_arguments(_arguments: Arguments):
    print(f"Corpus Path: {_arguments.corpus_path}")
    print(f"Minimum Token Length: {_arguments.min_token_length if _arguments.min_token_length is not None else 'No'}")
    print(f"Stopwords: {'Yes' if _arguments.stopwords is not None else 'No'}")
    print(f"Use Stemmer: {'Yes' if _arguments.use_potter_stemmer else 'No'}")
    print(f"Memory Threshold: {_arguments.memory_threshold}")
    print(f"Index Path: {_arguments.index_path}")
