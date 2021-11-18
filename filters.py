"""
Module that contains the filter functions to be added to the DocumentProcessor
"""
from typing import Callable

import Stemmer

from processor import ProcessedDocument, Token


def filter_token(condition: Callable[[Token], bool]):
    def _filter(document: ProcessedDocument):
        document.tokens = filter(condition, document.tokens)
        return document

    return _filter


def stemmer(language: str):
    stemmer_instance = Stemmer.Stemmer(language)

    def stem_word(token: Token):
        token.word = stemmer_instance.stemWord(token.word)
        return token

    def stem(document: ProcessedDocument):
        document.tokens = (stem_word(token) for token in document.tokens)
        return document

    return stem
