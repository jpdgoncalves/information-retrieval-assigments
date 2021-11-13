from typing import List, Callable

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
    tokens: List[Token]


class DocumentProcessor:
    def __init__(self):
        self.processors: List[Callable[[ProcessedDocument], ProcessedDocument]] = []

    def process(self, costumer_review: CostumerReview) -> ProcessedDocument:
        content = regex_pattern.sub(" ", costumer_review.content)
        words = content.split(" ")
        tokens = [Token(word, pos) for pos, word in enumerate(words)]
        processed_document = ProcessedDocument(costumer_review.review_id, tokens)

        for processor in self.processors:
            processed_document = processor(processed_document)

        return processed_document

    def add_filter(self, _filter: Callable[[ProcessedDocument], ProcessedDocument]):
        self.processors.append(_filter)
