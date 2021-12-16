"""
Module containing the DocumentProcessor.
"""
import Stemmer
from typing import Set, Callable

from definitions import RawReview, ProcessedReview

import re


_regex_pattern = re.compile("[^a-z]")
_stemmer = Stemmer.Stemmer("english")


def english_stemmer(word: str):
    return _stemmer.stemWord(word)


def no_stemmer(word: str):
    return word


def review_processor(
        min_token_len: int,
        stopwords: Set[str],
        stemmer: Callable[[str], str],
):
    def process_review(raw_review: RawReview) -> ProcessedReview:
        doc_id, review_id, content = raw_review

        words = _regex_pattern.sub(" ", content.lower()).split(" ")
        words = [stemmer(word) for word in words if min_token_len <= len(word) < 50 and word not in stopwords]

        tokens = [(word, pos) for pos, word in enumerate(words)]
        doc_length = len(tokens)

        return (
            doc_id,
            review_id,
            tokens,
            doc_length
        )

    return process_review
