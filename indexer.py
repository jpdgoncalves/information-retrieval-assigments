from typing import List

from dictionary import PostingsDictionary
from processor import ProcessedDocument

import spimi


class SpimiIndexer:
    def __init__(self, index_name: str):
        self.index_name = index_name
        self.block_names: List[str] = []

    def add_review(self, review: ProcessedDocument):
        pass

    def create_index_file(self):
        spimi.merge_blocks(self.index_name, self.block_names)