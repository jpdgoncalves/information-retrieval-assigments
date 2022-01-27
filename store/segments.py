import os
from typing import List

from definitions import TermPostingsEntry, Segment

from . import postings
from . import vocabulary


def segment_formatter(postings_write: callable, vocab_write: callable, **props):
    def write_segment(
            vocab_path: str,
            postings_path: str,
            entries: List[TermPostingsEntry]
    ):
        terms, l_postings = tuple(zip(*entries))
        offsets = postings_write(postings_path, l_postings, **props)
        vocab_write(vocab_path, terms, *offsets)

    return write_segment


def tf_idf_format(review_count: int):
    return segment_formatter(
        postings.write_tf_idf_postings,
        vocabulary.write_tf_idf_vocabulary,
        review_count=review_count
    )


def bm25_format(
        review_count: int,
        avg_dl: float,
        document_lengths: List[int],
        b: float,
        k1: float
):
    return segment_formatter(
        postings.write_bm25_postings,
        vocabulary.write_bm25_vocabulary,
        review_count=review_count,
        avg_dl=avg_dl,
        document_lengths=document_lengths,
        b=b, k1=k1
    )


def read_segments(segments_dir_path: str) -> List[Segment]:
    segment_paths = []

    for segment_path in sorted(os.listdir(segments_dir_path)):
        first_term, last_term = segment_path.split("-")
        segment_paths.append((first_term, last_term, f"{segments_dir_path}/{segment_path}"))

    return segment_paths
