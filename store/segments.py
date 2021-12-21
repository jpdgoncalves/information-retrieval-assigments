from typing import List
from definitions import TermPostingsEntry

import math


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
        postings_entries = []
        vocabulary_entries = []

        for term, postings in entries:
            postings_portions = []
            prev_doc_id = 0
            idf = math.log10(review_count / len(postings))

            for doc_id, (weight, positions) in postings:
                postings_portions.append(
                    f"{doc_id - prev_doc_id}:{weight}:{','.join(str(pos) for pos in positions)}"
                )
                prev_doc_id = doc_id

            posting_entry = ";".join(postings_portions)
            byte_len = len(posting_entry.encode("utf-8")) + 1  # needed for the \n
            vocab_entry = f"{term}:{idf}:{offset}:{byte_len}"

            postings_entries.append(posting_entry)
            vocabulary_entries.append(vocab_entry)

            offset += byte_len

        postings_file.writelines(postings_entries)
        vocab_file.writelines(vocabulary_entries)


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
            open(postings_path, "wb") as postings_file:

        offset = 0

        for term, postings in entries:
            postings_portions = []
            writen_bytes = 0
            prev_doc_id = 0
            idf = math.log10(review_count / len(postings))

            for doc_id, (tf, positions) in postings:
                b_normalizer = 1 - b + b * (document_lengths[doc_id] / avg_dl)
                weight = idf * ((k1 + 1) * tf) / (k1 * b_normalizer + tf)
                postings_portions.append(
                    f"{doc_id - prev_doc_id}:{weight}:{','.join(str(pos) for pos in positions)}"
                )
                prev_doc_id = doc_id

            writen_bytes += postings_file.write(bytes(';'.join(postings_portions), encoding="utf-8"))
            writen_bytes += postings_file.write(b"\n")
            vocab_file.write(f"{term}:{idf}:{offset}:{writen_bytes}\n")
            offset += writen_bytes
