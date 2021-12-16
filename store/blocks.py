from typing import List, Optional, Generator
from definitions import Vocabulary, TermPostingsEntry

import heapq
import pickle


def write_block(block_path: str, vocabulary: Vocabulary):
    with open(block_path, "wb") as block_file:
        print(f"[BlockWriter]: Writing {block_path}")

        sorted_terms = sorted(vocabulary.keys())

        for term in sorted_terms:
            pickle.dump((term, vocabulary[term]), block_file, pickle.HIGHEST_PROTOCOL)

        print(f"[BlockWriter]: Finished writing {block_path}")


class BlockFile:

    def __init__(self, block_path: str):
        self.block_path = block_path
        self.block_file = open(block_path, "rb")
        self._next_entry: TermPostingsEntry = self._read_one()

    def _read_one(self) -> Optional[TermPostingsEntry]:
        try:
            return pickle.load(self.block_file)
        except EOFError:
            return None

    def read(self) -> Optional[TermPostingsEntry]:
        entry = self._next_entry
        self._next_entry = self._read_one()

        return entry

    def eof(self):
        return self._next_entry is None

    def close(self):
        self.block_file.close()

    # noinspection PyProtectedMember
    def __lt__(self, other):
        this_term = self._next_entry[0]
        other_term = other._next_entry[0]
        this_first_doc_id = self._next_entry[1][0][0]
        other_first_doc_id = other._next_entry[1][0][0]

        return (this_term, this_first_doc_id) < (other_term, other_first_doc_id)

    def __repr__(self):
        return f"{self._next_entry[0]}"


def blocks_iterator(block_names: List[str]) -> Generator[TermPostingsEntry, None, None]:
    block_files = [BlockFile(block_name) for block_name in block_names]
    heapq.heapify(block_files)

    while len(block_files) != 0:
        # print(block_files)
        block_file = heapq.heappop(block_files)
        entry = block_file.read()

        if not block_file.eof():
            heapq.heappush(block_files, block_file)
        else:
            block_file.close()

        yield entry
