from dataclasses import dataclass
from typing import (
    Iterable, DefaultDict, Tuple,
    List, Callable, Dict, Generator
)


@dataclass
class IndexingStatistics:
    indexing_time: float
    index_size_on_disk: int
    term_count: int
    review_count: int
    blocks_used: int


ReviewId = str
DocId = int
Weight = float
Position = int
DocLength = int
Term = str

RawReview = Tuple[DocId, ReviewId, str]
Token = Tuple[Term, Position]
ProcessedReview = Tuple[DocId, ReviewId, Iterable[Token], DocLength]

Posting = Tuple[Weight, List[Position]]
Postings = List[Tuple[DocId, Posting]]
Vocabulary = DefaultDict[Term, Postings]
TermIndex = Dict[Term, List[Position]]
TermPostings = Dict[Term, Posting]
TermPostingsEntry = Tuple[Term, Postings]

RawReviewReader = Generator[RawReview, None, None]
Processor = Callable[[RawReview], ProcessedReview]
WeightFunction = Callable[[TermIndex], TermPostings]
SegmentWriteFormat = Callable[[str, str, List[TermPostingsEntry]], None]
