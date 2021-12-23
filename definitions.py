from dataclasses import dataclass
from enum import Enum
from typing import (
    DefaultDict, Tuple, Set, TypedDict,
    List, Callable, Dict, Generator
)


class IndexingFormat(Enum):
    TF_IDF = "tf_idf"
    BM25 = "bm25"
    NO_INDEX = "none"


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
SearchResults = List[Tuple[ReviewId, float]]


@dataclass
class IndexProperties:
    idx_format: IndexingFormat  # is a string on disk
    index_size_on_disk: int
    term_count: int
    review_count: int
    min_token_length: int
    stopwords: Set[str]  # a string of words separated by commas
    stemmer: StemmerFunction


class IndexPropsDict(TypedDict):
    idx_format: str
    index_size_on_disk: int
    term_count: int
    review_count: int
    min_token_length: int
    stopwords: List[str]  # a string of words separated by commas
    stemmer: str
