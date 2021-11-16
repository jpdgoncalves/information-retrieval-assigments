"""
Module containing a simple helper Data Structure that handles the construction
of an inverted dictionary.
"""
from typing import DefaultDict, List

from collections import defaultdict

from processor import ProcessedDocument

Postings = DefaultDict[str, List[int]]


def postings():
    return defaultdict(list)


class PostingsDictionary:
    def __init__(self):
        self.postings_list: DefaultDict[str, Postings] = defaultdict(postings)

    def add_document(self, document: ProcessedDocument):
        for token in document.tokens:
            self.postings_list[token.word][document.id].append(token.pos)
