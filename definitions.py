from dataclasses import dataclass
from typing import (
    DefaultDict, Tuple,
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
Length = int
Term = str

RawReview = Tuple[DocId, ReviewId, str]
Token = Tuple[Term, Position]

Posting = Tuple[Weight, List[Position]]
Postings = List[Tuple[DocId, Posting]]
Vocabulary = DefaultDict[Term, Postings]
TermIndex = Dict[Term, List[Position]]
TermPostings = Dict[Term, Posting]
TermPostingsEntry = Tuple[Term, Postings]

ProcessedReview = Tuple[DocId, ReviewId, TermPostings, Length]
ProcessedQuery = Tuple[Length, TermIndex]

RawReviewReader = Generator[RawReview, None, None]
StemmerFunction = Callable[[str], str]
Processor = Callable[[RawReview], ProcessedReview]
WeightFunction = Callable[[TermIndex], TermPostings]
SegmentWriteFormat = Callable[[str, str, List[TermPostingsEntry]], None]

Path = str
Idf = float
Offset = int
PostingLen = int

Segment = Tuple[Term, Term, Path]
IdfMetadata = Tuple[Path, Idf, Offset, PostingLen]
BM25Metadata = Tuple[Path, Offset, PostingLen]
PostingResults = List[Tuple[DocId, Weight, List[Position]]]