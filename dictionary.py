"""
Module containing a simple helper Data Structure that handles the construction
of an inverted dictionary.
"""
from typing import List
from definitions import (
    ProcessedReview,
    ReviewId, Vocabulary, Postings,
)

from collections import defaultdict


def _postings() -> Postings:
    return []


class PostingsDictionary:
    def __init__(self):
        self.review_ids: List[ReviewId] = []
        self.postings_list: Vocabulary = defaultdict(_postings)

    def add_document(self, review: ProcessedReview):
        doc_id, review_id, postings, _ = review
        self.review_ids.append(review_id)

        for term, (weight, positions) in postings.items():
            self.postings_list[term].append((doc_id, weight, positions))
