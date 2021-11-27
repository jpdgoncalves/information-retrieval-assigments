"""
Module containing a indexer that implements SPIMI.
"""

import psutil
import gc
import os

from dictionary import PostingsDictionary
from processor import ProcessedDocument
from spimi.blocks import BlockWriter
from spimi.merger import merge_blocks


def _ensure_paths(index_path: str):
    if os.path.exists(index_path):
        raise FileExistsError(f"File or Directory at {index_path} already exists")

    blocks_path = f"{index_path}/blocks"
    segments_path = f"{index_path}/segments"

    os.mkdir(index_path)
    os.mkdir(blocks_path)
    os.mkdir(segments_path)

    return blocks_path, segments_path


class SpimiIndexer:
    def __init__(self, index_path: str, memory_threshold: float):
        """
        Creates a SpimiIndexer. The intended use of this class is that
        for each processed review the method add_review is called until
        all reviews are processed. Then at the end call the create_index_file method
        to create the final index.
        :param index_path: The path of the index.
        :param memory_threshold: The amount of memory to be used as decimal between 0 and 1.
        For example 0.5 would mean 50% of the memory available.
        """
        blocks_path, segments_path = _ensure_paths(index_path)

        self.index_path = index_path
        self.review_ids_path = f"{index_path}/review_ids.txt"
        self.blocks_path = blocks_path
        self.segments_path = segments_path
        self.block_writer = BlockWriter(
            self.review_ids_path,
            blocks_path,
            "block_"
        )
        self.postings_dictionary = PostingsDictionary()
        self.memory_threshold = memory_threshold
        self.index_disk_size = 0
        self.term_count = 0
        self.review_count = 0

        self._self_process = psutil.Process()
        self._review_count_for_mem_check = 100

    @property
    def blocks_used(self):
        return self.block_writer.block_count

    @property
    def block_names(self):
        return self.block_writer.block_names

    @property
    def f_index_disk_size(self):
        mega_bytes = self.index_disk_size / (1024 * 1024)
        return f"{mega_bytes:.2f}MB"

    def add_review(self, review: ProcessedDocument):
        self.review_count += 1
        self.postings_dictionary.add_document(review)

        if self.review_count % self._review_count_for_mem_check == 0 and not self._has_memory():
            self.create_block_and_new_dictionary()

    def create_index_file(self):
        self.create_block_and_new_dictionary()

        self.term_count = merge_blocks(self.index_path, self.block_names)
        self.index_disk_size = os.path.getsize(self.index_path)

        for block_name in self.block_names:
            os.remove(block_name)

    def create_block_and_new_dictionary(self):
        block_name = self.block_writer.write_block(self.postings_dictionary)
        self.block_names.append(block_name)
        self.postings_dictionary = PostingsDictionary()
        gc.collect()

    def _has_memory(self):
        used_memory = self._self_process.memory_info().vms
        total_memory = psutil.virtual_memory().total

        return (used_memory / total_memory) < self.memory_threshold
