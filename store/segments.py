"""
segment_list.txt
segments/
    aa-aabb/
        vocabulary.txt
        postings.txt
    aabc-bb/
        vocabulary.txt
        postings.txt
    ...

make the segments small enough so they can quickly loaded into memory when needed.
So each directory will contain around 5000 terms. Should be quick enough to scan through for the pointer to the postings

There are two different formats for the vocabulary.txt
term:idf:posting_offset:posting_length
term:posting_offset:posting_length

Need to calculate weights while writing segments for bm25
Don't need to calculate anything for tf-idf

How to use the segments.py

segments_format = segments.tf_idf_format(document_count)
index_segments_writer = IndexSegmentsWriter(
    segment_dir,
    write_format
)
"""
from typing import List, Callable
from definitions import TermPostingsEntry, Term, Postings

import math
import os


class SegmentWriter:
    def __init__(
            self,
            segment_path: str,
            first_term: Term,
            write_format: Callable
    ):
        self.terms: List[Term] = [first_term]
        self.postings: Postings = []

        self.writen_bytes = 0
        self._write_format = write_format
        self.vocab_file = open(f"{segment_path}/vocabulary.txt", "w", encoding="utf-8")
        self.postings_file = open(f"{segment_path}/postings.txt", "wb")

    @property
    def current_term(self):
        return self.terms[-1]

    @property
    def term_count(self):
        return len(self.terms)

    def write(self, entry: TermPostingsEntry):
        term, postings = entry

        if self.current_term != term:
            self._write_format(self)
            self.terms.append(term)
            self.postings.clear()

        self.postings.extend(postings)

    def write_to_vocab(self, entry: str):
        self.vocab_file.write(entry)

    def write_to_postings(self, entry: str):
        writen_bytes = self.postings_file.write(bytes(entry, "utf-8"))
        self.writen_bytes += writen_bytes
        return writen_bytes

    def close(self):
        self.vocab_file.close()
        self.postings_file.close()


def tf_idf_format(document_count: int):
    def _write_format(segment_writer: SegmentWriter):
        term = segment_writer.current_term
        idf = math.log10(document_count / len(segment_writer.postings))
        offset = segment_writer.writen_bytes
        postings_entry = []

        for doc_id, (weight, positions) in segment_writer.postings:
            postings_entry.append(f"{doc_id}:{weight}:{','.join(str(pos) for pos in positions)}")

        length = segment_writer.write_to_postings(';'.join(postings_entry))
        segment_writer.write_to_vocab(f"{term}:{idf}:{offset}:{length}")

    return _write_format


def bm25_format(
        document_count: int,
        avg_dl: float,
        document_lengths: List[int],
        b: float,
        k1: float
):
    def _write_format(segment_writer: SegmentWriter):
        term = segment_writer.current_term
        idf = math.log10(document_count / len(segment_writer.postings))
        offset = segment_writer.writen_bytes
        postings_entry = []

        for doc_id, (tf, positions) in segment_writer.postings:
            b_normalizer = 1 - b + b * (document_lengths[doc_id] / avg_dl)
            weight = idf * ((k1 + 1) * tf) / (k1 * b_normalizer + tf)
            postings_entry.append(f"{doc_id}:{weight}:{','.join(str(pos) for pos in positions)}")

        length = segment_writer.write_to_postings(';'.join(postings_entry))
        segment_writer.write_to_vocab(f"{term}:{offset}:{length}")

    return _write_format


class IndexSegmentsWriter:
    def __init__(
            self,
            segments_dir: str,
            write_format: Callable,
            terms_per_segment: int = 1000
    ):
        self.segments_dir = segments_dir
        self.write_format = write_format
        self.terms_per_segment = terms_per_segment
        self.term_count = 0
        self.segments: List[str] = []
        self.segment_writer = None

    @property
    def segment_count(self):
        return len(self.segments)

    def _get_temp_segment_name(self):
        return f"{self.segments_dir}/segment_{self.segment_count}/"

    def _get_segment_name(self):
        return f"{self.segments_dir}/{self.segment_writer.terms[0]}-{self.segment_writer.terms[-1]}"

    def write(self, entry: TermPostingsEntry):
        if self.segment_writer is None:
            self.segment_writer = SegmentWriter(
                self._get_temp_segment_name(),
                entry[0],
                self.write_format
            )

        self.segment_writer.write(entry)

        if self.segment_writer.term_count >= self.terms_per_segment:
            self._close_segment()

    def _close_segment(self):
        self.segment_writer.close()

        segment_name = self._get_segment_name()
        os.rename(self._get_temp_segment_name(), segment_name)

        self.segments.append(segment_name)
        self.term_count += self.segment_writer.term_count
        self.segment_writer = None
        print(f"[IndexSegmentWriter]: Wrote segment {segment_name}")

    def close(self):
        self._close_segment()
