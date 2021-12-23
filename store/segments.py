import math
import os
from typing import List

from definitions import TermPostingsEntry, Segment


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
            open(postings_path, "w", encoding="utf-8", newline="\n") as postings_file:

        offset = 0
        postings_portions = []
        vocabulary_portions = []

        for term, postings in entries:
            prev_doc_id = 0
            byte_len = 0
            postings_count = len(postings)
            idf = math.log10(review_count / postings_count)

            for i, (doc_id, (weight, positions)) in enumerate(postings):
                posting_portion = f"{doc_id - prev_doc_id}:{weight}:{','.join(str(pos) for pos in positions)}"
                byte_len += len(posting_portion.encode("utf-8"))  # Length of this posting in bytes

                postings_portions.append(posting_portion)

                if i != postings_count - 1:
                    postings_portions.append(";")
                    byte_len += 1  # Adding the length of the semicolon.

                prev_doc_id = doc_id

            postings_portions.append("\n")  # End of the postings for this term
            byte_len += 1  # needed for the \n

            vocabulary_portions.append(f"{term}:{idf}:{offset}:{byte_len}\n")
            offset += byte_len

        postings_file.writelines(postings_portions)
        vocab_file.writelines(vocabulary_portions)


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
            open(postings_path, "w", encoding="utf-8", newline="\n") as postings_file:

        offset = 0
        postings_portions = []
        vocabulary_portions = []

        for term, postings in entries:
            byte_len = 0
            prev_doc_id = 0
            postings_count = len(postings)
            idf = math.log10(review_count / postings_count)

            for i, (doc_id, (tf, positions)) in enumerate(postings):

                b_normalizer = 1 - b + b * (document_lengths[doc_id] / avg_dl)
                weight = idf * ((k1 + 1) * tf) / (k1 * b_normalizer + tf)

                posting_portion = f"{doc_id - prev_doc_id}:{weight}:{','.join(str(pos) for pos in positions)}"
                byte_len += len(posting_portion.encode("utf-8"))  # Byte size of the posting

                postings_portions.append(posting_portion)

                if i != postings_count - 1:
                    postings_portions.append(";")
                    byte_len += 1  # Byte size of the ;

                prev_doc_id = doc_id

            postings_portions.append("\n")  # End of the postings for this term
            byte_len += 1  # needed for the \n

            vocabulary_portions.append(f"{term}:{offset}:{byte_len}\n")
            offset += byte_len

        postings_file.writelines(postings_portions)
        vocab_file.writelines(vocabulary_portions)


def read_segments(segments_dir_path: str) -> List[Segment]:
    segment_paths = []

    for segment_path in sorted(os.listdir(segments_dir_path)):
        first_term, last_term = segment_path.split("-")
        segment_paths.append((first_term, last_term, f"{segments_dir_path}/{segment_path}"))

    return segment_paths
