"""
Module containing the DocumentProcessor.
"""
from typing import List

from corpus import CostumerReview
from definitions import Token, ProcessedDocument, Processor

import re


regex_pattern = re.compile("[^a-z]")


class ReviewProcessor:
    def __init__(self):
        self.processors: List[Processor] = []

    def process(self, costumer_review: CostumerReview) -> ProcessedDocument:
        """
        Processes the specified CostumerReview into a ProcessedDocument.
        It first applies some basic tokenization and generates an instance of
        ProcessedDocument. Then it applies a list of filtering functions, by the order,
        they were added and returns the final ProcessedDocument instance at the end.
        """
        content = regex_pattern.sub(" ", costumer_review.content)
        words = (word for word in content.split(" ") if 0 < len(word) < 50)

        for processor in self.processors:
            words = processor(words)

        tokens = [Token(word, pos) for pos, word in enumerate(words)]
        document_length = len(tokens)

        return ProcessedDocument(
            costumer_review.doc_id,
            costumer_review.review_id,
            tokens,
            document_length
        )

    def add_filter(self, _filter: Processor):
        """
        Adds a filter function to the Document Processor. This functions are intended to,
        perform some modification to the contents of the ProcessedDocument given to them and return
        that same instance at the end.
        """
        self.processors.append(_filter)
