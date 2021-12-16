"""
Module containing a simple helper Data Structure that handles the construction
of an inverted dictionary.
"""
from typing import List, Iterable
from definitions import (
    ProcessedReview, Token,
    ReviewId, Vocabulary, Postings,
    WeightFunction, TermIndex, TermPostings
)

from collections import defaultdict

import math


def _postings() -> Postings:
    return []


def _aggregate(tokens: Iterable[Token]) -> TermIndex:
    postings = defaultdict(list)

    for word, pos in tokens:
        postings[word].append(pos)

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

    def add_document(self, review: ProcessedReview):
        doc_id, review_id, tokens, _ = review
        term_index = _aggregate(tokens)
        postings = self.weight_function(term_index)

        self.review_ids.append(review_id)

        for term, posting in postings.items():
            self.postings_list[term].append((doc_id, posting))


def tf_idf_dictionary():
    return PostingsDictionary(normalized_tf_weight_function)


def term_count_dictionary():
    return PostingsDictionary(term_count_function)
