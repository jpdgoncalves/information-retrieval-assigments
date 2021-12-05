"""
Module containing a simple helper Data Structure that handles the construction
of an inverted dictionary.
"""
from typing import List
from definitions import (
    ProcessedDocument,
    ReviewId, Vocabulary, Postings,
    WeightFunction, TermIndex, TermPostings
)

from collections import defaultdict

import math


def _postings() -> Postings:
    return {}


def _aggregate(document: ProcessedDocument) -> TermIndex:
    postings = defaultdict(list)

    for token in document.tokens:
        postings[token.word].append(token.pos)

    return postings


# noinspection PyTypeChecker
def normalized_tf_weight_function(term_index: TermIndex) -> TermPostings:
    postings = {}

    for term, positions in term_index.items():
        postings[term] = 1 + math.log10(len(positions))

    total_squared_score = sum(score ** 2 for score in postings.values())
    score_normalizer = math.sqrt(total_squared_score)

    for term, positions in term_index.items():
        postings[term] = (postings[term] / score_normalizer, positions)

    return postings


# noinspection PyTypeChecker
def term_count_function(term_index: TermIndex) -> TermPostings:
    postings = {}

    for term, positions in term_index.items():
        postings[term] = (len(positions), positions)

    return postings


class PostingsDictionary:
    def __init__(self, weight_function: WeightFunction):
        self.review_ids: List[ReviewId] = []
        self.postings_list: Vocabulary = defaultdict(_postings)
        self.weight_function = weight_function

    def add_document(self, document: ProcessedDocument):
        term_index = _aggregate(document)
        postings = self.weight_function(term_index)

        self.review_ids.append(document.review_id)

        for term, posting in postings.items():
            self.postings_list[term][document.id] = posting


def tf_idf_dictionary():
    return PostingsDictionary(normalized_tf_weight_function)


def term_count_dictionary():
    return PostingsDictionary(term_count_function)