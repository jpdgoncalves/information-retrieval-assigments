from typing import List

import psutil
import gc

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
        if not self._has_memory():
            self.create_block_and_new_dictionary()

        self.postings_dictionary.add_document(review)

    def create_index_file(self):
        self.create_block_and_new_dictionary()
        spimi.merge_blocks(self.index_name, self.block_names)

    def create_block_and_new_dictionary(self):
        block_name = self.write_block(self.postings_dictionary)
        self.block_names.append(block_name)
        self.postings_dictionary = PostingsDictionary()
        gc.collect()

    def _has_memory(self):
        virtual_memory = psutil.virtual_memory()
        total_memory = virtual_memory.total
        available = virtual_memory.available

        return 1 - (available / total_memory) < self.memory_threshold
