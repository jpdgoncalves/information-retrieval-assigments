"""
This module handles the parsing of the command arguments into an instance
of Arguments. This instance intends to provide type hints which we wouldn't
get if we returned the original Namespace object from argparse module.
"""
import os
from typing import Set

from argparse import ArgumentParser
from dataclasses import dataclass

from definitions import IndexingFormat


@dataclass
class Arguments:
    corpus_path: str
    min_token_length: int
    stopwords: Set[str]
    use_potter_stemmer: bool
    memory_threshold: float
    index_path: str
    indexing_format: IndexingFormat
    debug_mode: bool
    index_only: bool
    k1: float
    b: float
    queries_path: str
    queries_rev_path: str
    results_path: str
    evaluation_path: str
    query_limit: int


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
    with open(_existing_path(file_path), encoding="utf-8") as sw_file:
        for word in sw_file:
            stopwords.add(word.strip())

    return stopwords


def _existing_path(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} is not a file")

    return file_path


default_arguments = {
    "min_token_length": 3,
    "stopwords": _read_stopwords_file("data/stopwords.txt"),
    "use_potter_stemmer": True,
    "memory_threshold": 0.5,
    "index_path": "results/segmented_index",
    "indexing_format": IndexingFormat.TF_IDF,
    "debug_mode": False,
    "index_only": False,
    "k1": 1.2,
    "b": 0.75,
    "corpus_path": "data/amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz",
    "queries_path": "data/queries.txt",
    "query_rev_path": "data/queries.relevance.txt",
    "results_path": "results/results.txt",
    "evaluation_path": "results/evaluation.txt",
    "query_limit": 100
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
    const=0
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
    const=set()
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
    "-out", "--index-path",
    dest="index_path",
    default=default_arguments["index_path"]
)

# Handling indexing format
arg_parser.add_argument(
    "-if", "--indexing-format",
    dest="indexing_format",
    type=IndexingFormat,
    default=default_arguments["indexing_format"]
)

# Sets script into debug mode
arg_parser.add_argument(
    "-d", "--debug",
    dest="debug_mode",
    action="store_true",
    default=default_arguments["debug_mode"]
)

# Sets script to index only mode
arg_parser.add_argument(
    "--index-only",
    dest="index_only",
    action="store_true",
    default=default_arguments["index_only"]
)

# BM25 Parameters
arg_parser.add_argument(
    "-k1",
    dest="k1",
    type=float,
    default=default_arguments["k1"]
)

arg_parser.add_argument(
    "-b",
    dest="b",
    type=float,
    default=default_arguments["b"]
)


# Handling corpus path
arg_parser.add_argument(
    "-in", "--corpus-path",
    dest="corpus_path",
    type=_existing_path,
    default=default_arguments["corpus_path"]
)

# Handling queries path
arg_parser.add_argument(
    "-qp", "--queries-path",
    dest="queries_path",
    type=_existing_path,
    default=default_arguments["queries_path"]
)

# Handling results path
arg_parser.add_argument(
    "-rp", "--results-path",
    dest="results_path",
    default=default_arguments["results_path"]
)

# Handling of evaluation parameters
arg_parser.add_argument(
    "-qrp", "--queries-relevance-path",
    dest="queries_rev_path",
    type=_existing_path,
    default=default_arguments["query_rev_path"]
)

arg_parser.add_argument(
    "-ep", "--evaluation-path",
    dest="evaluation_path",
    default=default_arguments["evaluation_path"]
)

arg_parser.add_argument(
    "-ql", "--query-limit",
    dest="query_limit",
    type=int,
    default=default_arguments["query_limit"]
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
        arg_values.index_path,
        arg_values.indexing_format,
        arg_values.debug_mode,
        arg_values.index_only,
        arg_values.k1,
        arg_values.b,
        arg_values.queries_path,
        arg_values.queries_rev_path,
        arg_values.results_path,
        arg_values.evaluation_path,
        arg_values.query_limit
    )


def print_arguments(_arguments: Arguments):
    print(f"Corpus Path: {_arguments.corpus_path}")
    print(f"Minimum Token Length: {_arguments.min_token_length if _arguments.min_token_length is not None else 'No'}")
    print(f"Stopwords: {'Yes' if _arguments.stopwords is not None else 'No'}")
    print(f"Use Stemmer: {'Yes' if _arguments.use_potter_stemmer else 'No'}")
    print(f"Memory Threshold: {_arguments.memory_threshold}")
    print(f"Index Path: {_arguments.index_path}")
    print(f"Indexing Format: {_arguments.indexing_format.value}")
    print(f"BM25 Parameters: k1={_arguments.k1} b={_arguments.b}")
    print(f"Debug Mode: {'Yes' if _arguments.debug_mode else 'No'}")
    print(f"Index Only: {'Yes' if _arguments.index_only else 'No'}")
    print(f"Queries Path: {_arguments.queries_path}")
    print(f"Results Path: {_arguments.results_path}")
    print(f"Evaluation Path: {_arguments.evaluation_path}")
    print(f"Queries Relevance Path: {_arguments.queries_rev_path}")
    print(f"Query Results Limit: {'No' if _arguments.query_limit < 1 else _arguments.query_limit}")
