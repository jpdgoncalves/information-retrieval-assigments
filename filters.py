"""
Module that contains the filter functions to be added to the DocumentProcessor
"""
from typing import Callable

import Stemmer

from processor import ProcessedDocument, Token


def filter_token(condition: Callable[[Token], bool]):
    def _filter(document: ProcessedDocument):
        document.tokens = list(filter(condition, document.tokens))
        return document

    return _filter


def stemmer(language: str):
    stemmer_instance = Stemmer.Stemmer(language)

    def stem(document: ProcessedDocument):
        for token in document.tokens:
            token.word = stemmer_instance.stemWord(token.word)
        return document

    return stem
