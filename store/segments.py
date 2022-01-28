import os
from typing import List

from definitions import TermPostingsEntry, Segment, PostsFormat, VocabFormat, SegmentFormat

from . import postings
from . import vocabulary
from .index import IndexDirectory


def segment_formatter(postings_write: PostsFormat, vocab_write: VocabFormat, **props):
    def write_segment(
            vocab_path: str,
            postings_path: str,
            entries: List[TermPostingsEntry]
    ):
        terms, l_postings = tuple(zip(*entries))
        offsets = postings_write(postings_path, l_postings, **props)
        vocab_write(vocab_path, terms, *offsets)

    return write_segment


class BufferedSegmentWriter:
    def __init__(
            self, segment_format: SegmentFormat, index_directory: IndexDirectory,
            n_terms_per_seg=50000,
    ):
        self.index_dir = index_directory
        self.write_segment = segment_format

        self.posts_buffer: List[TermPostingsEntry] = []
        self.n_terms_per_seg = n_terms_per_seg
        self.buffer_count = 0
        self.term_count = 0

    def write(self, entry: TermPostingsEntry):
        if self.buffer_count < self.n_terms_per_seg:
            self.posts_buffer.append(entry)
            self.buffer_count += 1
            self.term_count += 1
        else:
            self.flush()
            self.posts_buffer.append(entry)

    def flush(self):
        first_term = self.posts_buffer[0][0]
        last_term = self.posts_buffer[-1][0]
        segment_path, vocab_path, postings_path = self.index_dir.make_segment_dir(first_term, last_term)

        print(f"[SegmentWriter] Writing segment {segment_path}")
        self.write_segment(vocab_path, postings_path, self.posts_buffer)
        print(f"[SegmentWriter] Finished writing {segment_path}")

        self.posts_buffer = []
        self.buffer_count = 0


def tf_idf_format(review_count: int):
    return segment_formatter(
        postings.write_bm25_postings,
        vocabulary.write_bm25_vocabulary,
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
