from typing import List

from dictionary import PostingsDictionary
from processor import ProcessedDocument

import spimi


class SpimiIndexer:
    def __init__(self, index_name: str, memory_threshold: float):
        """
        Creates a SpimiIndexer that can be called iteratively
        on each document.
        :param index_name: The name of the final merged index
        :param memory_threshold: The amount of memory to be used as decimal between 0 and 1.
        For example 0.5 would mean 50% of the memory available.
        """
        self.index_name = index_name
        self.block_names: List[str] = []
        self.write_block = spimi.block_writer("block")
        self.postings_dictionary = PostingsDictionary()
        self.memory_threshold = memory_threshold

    def add_review(self, review: ProcessedDocument):
        pass

    def create_index_file(self):
        spimi.merge_blocks(self.index_name, self.block_names)
