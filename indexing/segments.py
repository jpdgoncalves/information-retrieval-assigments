"""
This module contains a class that serves as the segmented index writer for the
indexing pipeline.

For testing purpose we will use term count to divide the segments.
"""
from typing import List
from definitions import SegmentWriteFormat, TermPostingsEntry

from store.index import IndexDirectory


class SegmentWriter:
    def __init__(
            self,
            index_directory: IndexDirectory,
            segment_writer: SegmentWriteFormat,
            term_limit: int = 5000
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
                _, vocab_path, postings_path = self.index_directory.make_segment_dir(self._first_term, self._last_term)
                self.segment_writer(vocab_path, postings_path, self._accumulated_entries)
                self._accumulated_entries = []

            self._accumulated_entries.append(entry)
            self.term_count += 1

        self._last_postings.extend(postings)

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
