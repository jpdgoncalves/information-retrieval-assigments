from typing import Iterable, DefaultDict, Tuple, List, Callable, Dict

from dataclasses import dataclass


class CostumerReview:
    def __init__(self, doc_id: int, review_id: str, product_title: str, review_headline: str, review_body: str):
        self.doc_id = doc_id
        self.review_id = review_id
        self.product_title = product_title
        self.review_headline = review_headline
        self.review_body = review_body

    @property
    def content(self):
        return f"{self.product_title} {self.review_headline} {self.review_body}"


class Token:
    def __init__(self, word: str, pos: int):
        self.word = word
        self.pos = pos


class ProcessedDocument:
    def __init__(self, _id: int, review_id: str, tokens: Iterable[Token], document_length: int):
        self.id = _id
        self.review_id = review_id
        self.tokens = tokens
        self.document_length = document_length


@dataclass
class IndexingStatistics:
    indexing_time: float
    index_size_on_disk: int
    term_count: int
    blocks_used: int


ReviewId = str
DocId = int
Weight = float
Position = int
DocLength = int
Term = str

Posting = Tuple[Weight, List[Position]]
Postings = List[Tuple[DocId, Posting]]
Vocabulary = DefaultDict[Term, Postings]
TermIndex = Dict[Term, List[Position]]
TermPostings = Dict[Term, Posting]
TermPostingsEntry = Tuple[Term, Postings]

Processor = Callable[[Iterable[str]], Iterable[str]]
WeightFunction = Callable[[TermIndex], TermPostings]
SegmentWriteFormat = Callable[[str, str, List[TermPostingsEntry]], None]
