"""
Module containing the DocumentProcessor.
"""
import math
import Stemmer
from collections import defaultdict
from typing import Set, Callable, List, Dict

from src.definitions import (
    RawReview, ProcessedReview, ProcessedQuery, Term, Idf,
    TermIndex, TermPostings, WeightFunction, StemmerFunction
)

import re


_regex_pattern = re.compile("[^a-z]")
_stemmer = Stemmer.Stemmer("english")


def query_processor(
        min_token_len: int,
        stopwords: Set[str],
        stemmer: Callable[[str], str]
):
    def process_query(query: str) -> ProcessedQuery:
        words = process_str(query, min_token_len, stopwords, stemmer)
        query_len = len(words)
        return query_len, aggregate(words)

    return process_query


def review_processor(
        min_token_len: int,
        stopwords: Set[str],
        stemmer: StemmerFunction,
        weight_function: WeightFunction
):
    def process_review(raw_review: RawReview) -> ProcessedReview:
        doc_id, review_id, content = raw_review

        words = process_str(content, min_token_len, stopwords, stemmer)
        postings = weight_function(aggregate(words))
        doc_length = len(words)

        return doc_id, review_id, postings, doc_length

    return process_review


def process_str(
        content: str,
        min_token_len: int,
        stopwords: Set[str],
        stemmer: Callable[[str], str],
):
    words = _regex_pattern.sub(" ", content.lower()).split(" ")
    return [stemmer(word) for word in words if min_token_len <= len(word) < 50 and word not in stopwords]


def aggregate(words: List[str]) -> TermIndex:
    count_dict = defaultdict(list)

    for position, word in enumerate(words):
        count_dict[word].append(position)

    return count_dict


def tf_term_index(term_index: TermIndex) -> TermPostings:
    postings = {}

    for term, positions in term_index.items():
        postings[term] = (1 + math.log10(len(positions)), positions)

    return postings


def normalize_term_postings(term_postings: TermPostings) -> TermPostings:
    normalized_postings = {}

    total_squared_score = sum(score ** 2 for score, _ in term_postings.values())
    score_normalizer = math.sqrt(total_squared_score)

    for term, (score, positions) in term_postings.items():
        normalized_postings[term] = (score / score_normalizer, positions)

    return normalized_postings


def normalized_tf_term_index(term_index: TermIndex) -> TermPostings:
    return normalize_term_postings(tf_term_index(term_index))


def normalized_tf_idf_term_index(
        term_index: TermIndex,
        term_idfs: Dict[Term, Idf]
) -> TermPostings:
    tf_postings = tf_term_index(term_index)
    tf_idf_postings = {}

    for term, (score, positions) in tf_postings.items():
        tf_idf_postings[term] = (term_idfs[term] * score, positions)

    return normalize_term_postings(tf_idf_postings)


def count_term_index(term_index: TermIndex) -> TermPostings:
    postings = {}

    for term, positions in term_index.items():
        postings[term] = (len(positions), positions)

    return postings


def english_stemmer(word: str):
    return _stemmer.stemWord(word)


def no_stemmer(word: str):
    return word
