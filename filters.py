"""
Module that contains the filter functions to be added to the DocumentProcessor
"""
from typing import Set, Iterable

import Stemmer


def filter_tokens_by_length(min_length: int):
    def _filter(tokens: Iterable[str]):
        return [token for token in tokens if len(token) >= min_length]

    return _filter


def filter_stopwords(stopwords: Set[str]):
    def _filter(tokens: Iterable[str]):
        return [token for token in tokens if token not in stopwords]

    return _filter


def stemmer(language: str):
    stemmer_instance = Stemmer.Stemmer(language)

    def stem(tokens: Iterable[str]):
        return [stemmer_instance.stemWord(token) for token in tokens]

    return stem
