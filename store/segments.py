import math
import os
from typing import List

from definitions import TermPostingsEntry, Segment
from .postings import serialize_as_postings


def tf_idf_format(review_count: int):
    def _write(
            vocab_path: str,
            postings_path: str,
            entries: List[TermPostingsEntry]
    ):
        _write_tf_idf_segment(vocab_path, postings_path, entries, review_count)

    return _write


def bm25_format(
        review_count: int,
        avg_dl: float,
        document_lengths: List[int],
        b: float,
        k1: float
):
    def _write(
            vocab_path: str,
            postings_path: str,
            entries: List[TermPostingsEntry]
    ):
        _write_bm25_segment(
            vocab_path, postings_path, entries,
            review_count, avg_dl, document_lengths, b, k1
        )

    return _write


def _write_tf_idf_segment(
        vocab_path: str,
        postings_path: str,
        entries: List[TermPostingsEntry],
        review_count: int
):
    with open(vocab_path, "w", encoding="utf-8") as vocab_file, \
            open(postings_path, "wb", buffering=1024 * 1024) as postings_file:

        offset = 0

        for term, postings in entries:
            postings_count = len(postings)
            idf = math.log10(review_count / postings_count)
            doc_ids, weights, l_positions = tuple(zip(*postings))
            doc_ids_diffs = [doc_ids[0]] + [doc_ids[i + 1] - doc_ids[i] for i in range(0, postings_count - 1)]

            byte_len = postings_file.write(
                f"{serialize_as_postings(doc_ids_diffs, weights, l_positions)}\n".encode("utf-8")
            )

            vocab_file.write(f"{term}:{idf}:{offset}:{byte_len}\n")
            offset += byte_len


def _write_bm25_segment(
        vocab_path: str,
        postings_path: str,
        entries: List[TermPostingsEntry],
        review_count: int,
        avg_dl: float,
        document_lengths: List[int],
        b: float,
        k1: float
):
    with open(vocab_path, "w", encoding="utf-8") as vocab_file, \
            open(postings_path, "wb", buffering=1024 * 1024) as postings_file:

        offset = 0

        for term, postings in entries:
            postings_count = len(postings)
            idf = math.log10(review_count / postings_count)
            doc_ids, tfs, l_positions = tuple(zip(*postings))
            doc_ids_diffs = [doc_ids[0]] + [doc_ids[i+1] - doc_ids[i] for i in range(0, postings_count-1)]
            doc_lens = [document_lengths[doc_id] for doc_id in doc_ids]
            weights = [_bm25_weight(avg_dl, doc_len, b, k1, idf, tf) for doc_len, tf in zip(doc_lens, tfs)]

            byte_len = postings_file.write(
                f"{serialize_as_postings(doc_ids_diffs, weights, l_positions)}\n".encode("utf-8")
            )

            vocab_file.write(f"{term}:{offset}:{byte_len}\n")
            offset += byte_len


def _bm25_weight(avg_dl: float, doc_len: int, b: float, k1: float, idf: float, tf: int):
    b_normalizer = 1 - b + b * (doc_len / avg_dl)
    return idf * ((k1 + 1) * tf) / (k1 * b_normalizer + tf)


def read_segments(segments_dir_path: str) -> List[Segment]:
    segment_paths = []

    for segment_path in sorted(os.listdir(segments_dir_path)):
        first_term, last_term = segment_path.split("-")
        segment_paths.append((first_term, last_term, f"{segments_dir_path}/{segment_path}"))

    return segment_paths
