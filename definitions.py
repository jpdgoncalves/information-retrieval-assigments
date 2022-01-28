from dataclasses import dataclass
from enum import Enum
from typing import (
    DefaultDict, Tuple, Set, TypedDict,
    List, Callable, Dict, Generator, Iterable, TextIO
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


Path = str

# Basic data types
ReviewId = str
DocId = int
Weight = float
Position = int
Length = int
Term = str

# Reader data types
RawReview = Tuple[DocId, ReviewId, str]
RawReviewReader = Generator[RawReview, None, None]

# Processor data types
Token = Tuple[Term, Position]
TermIndex = Dict[Term, List[Position]]
Posting = Tuple[Weight, List[Position]]
TermPostings = Dict[Term, Posting]

ProcessedReview = Tuple[DocId, ReviewId, TermPostings, Length]
ProcessedQuery = Tuple[Length, TermIndex]

Processor = Callable[[RawReview], ProcessedReview]
StemmerFunction = Callable[[str], str]
WeightFunction = Callable[[TermIndex], TermPostings]

# Inverted Dictionary data types
Postings = List[Tuple[DocId, Weight, List[Position]]]
Vocabulary = DefaultDict[Term, Postings]
TermPostingsEntry = Tuple[Term, Postings]

# Store data types
PostsFormat = Callable[[Path, List[Postings], ...], Tuple]
VocabFormat = Callable[[Path, List[Term], ...], None]
SegmentFormat = Callable[[str, str, List[TermPostingsEntry]], None]
Block = Tuple[Term, DocId, Postings, TextIO]


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


# Searching data types
Idf = float
Offset = int
PostingLen = int

Segment = Tuple[Term, Term, Path]
IdfMetadata = Tuple[Path, Idf, Offset, PostingLen]
BM25Metadata = Tuple[Path, Offset, PostingLen]
PostingResults = Iterable[Tuple[DocId, Weight, List[Position]]]
SearchResults = List[Tuple[ReviewId, float]]
