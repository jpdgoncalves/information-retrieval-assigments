"""
This module contains a class that serves as the segmented index writer for the
indexing pipeline.
"""
from typing import List
from definitions import SegmentWriteFormat, TermPostingsEntry

from store.index import IndexDirectory


class SegmentWriter:
    def __init__(
            self,
            index_directory: IndexDirectory,
            segment_writer: SegmentWriteFormat,
            term_limit: int = 50000
    ):
        self.index_directory = index_directory
        self.segment_writer = segment_writer
        self.term_limit = term_limit
        self.term_count = 0

        self._accumulated_entries: List[TermPostingsEntry] = []

    def write(self, entry: TermPostingsEntry):
        term, postings = entry

        if self._last_term != term:
            if self._is_full:
                self._write()

            self._accumulated_entries.append((term, []))
            self.term_count += 1

        self._last_postings.extend(postings)

    def flush(self):
        """Flushes the remaining accumulated postings"""
        self._write()

    def _write(self):
        segment_path, vocab_path, postings_path = self.index_directory.make_segment_dir(
            self._first_term, self._last_term
        )
        print(f"[SegmentWriter] Writing segment {segment_path}")
        self.segment_writer(vocab_path, postings_path, self._accumulated_entries)
        print(f"[SegmentWriter] Finished writing {segment_path}")
        self._accumulated_entries = []

    @property
    def _first_term(self):
        return self._accumulated_entries[0][0] if self._accumulated_entries else None

    @property
    def _last_term(self):
        return self._accumulated_entries[-1][0] if self._accumulated_entries else None

    @property
    def _last_postings(self):
        return self._accumulated_entries[-1][1] if self._accumulated_entries else None

    @property
    def _is_full(self):
        return len(self._accumulated_entries) == self.term_limit
