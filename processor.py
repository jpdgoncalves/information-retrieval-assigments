"""
Module containing the DocumentProcessor.
"""
from typing import List, Callable, Generator

from dataclasses import dataclass
from reader.corpus import CostumerReview

import re


regex_pattern = re.compile("[^a-z]")


@dataclass
class Token:
    word: str
    pos: int


@dataclass
class ProcessedDocument:
    id: str
    tokens: Generator[Token, None, None]


class DocumentProcessor:
    def __init__(self):
        self.processors: List[Callable[[ProcessedDocument], ProcessedDocument]] = []

    def process(self, costumer_review: CostumerReview) -> ProcessedDocument:
        """
        Processes the specified CostumerReview into a ProcessedDocument.
        It first applies some basic tokenization and generates an instance of
        ProcessedDocument. Then it applies a list of filtering functions, by the order,
        they were added and returns the final ProcessedDocument instance at the end.
        """
        content = regex_pattern.sub(" ", costumer_review.content)
        words = content.split(" ")
        tokens = (Token(word, pos) for pos, word in enumerate(words))
        processed_document = ProcessedDocument(costumer_review.review_id, tokens)

        for processor in self.processors:
            processed_document = processor(processed_document)

        return processed_document

    def add_filter(self, _filter: Callable[[ProcessedDocument], ProcessedDocument]):
        """
        Adds a filter function to the Document Processor. This functions are intended to,
        perform some modification to the contents of the ProcessedDocument given to them and return
        that same instance at the end.
        """
        self.processors.append(_filter)
