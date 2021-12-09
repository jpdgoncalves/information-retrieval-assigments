from typing import List, Optional, Generator
from definitions import Vocabulary, TermPostingsEntry

import heapq
import pickle


class BlockWriter:
    """
    Class with the functionality needed to write postings into
    blocks. It uses pickle format for faster loading when reading.
    """
    def __init__(self, block_dir_path: str, block_prefix: str):
        self.block_dir_path = block_dir_path
        self.block_prefix = block_prefix
        self.blocks_path_prefix = f"{block_dir_path}/{block_prefix}"
        self.block_paths: List[str] = []

    @property
    def block_count(self):
        return len(self.block_paths)

    def write(self, vocabulary: Vocabulary):
        block_name = self._generate_block_name()
        print(f"[BlockWriter]: Writing {block_name}")

        with open(block_name, "wb") as block_file:
            sorted_terms = sorted(vocabulary.keys())

            for term in sorted_terms:
                pickle.dump((term, vocabulary[term]), block_file, pickle.HIGHEST_PROTOCOL)

        self.block_paths.append(block_name)
        print(f"[BlockWriter]: Finished writing {block_name}")

    def _generate_block_name(self):
        return f"{self.blocks_path_prefix}{self.block_count}.pickle"


class BlockFile:

    def __init__(self, block_path: str):
        self.block_path = block_path
        self.block_file = open(block_path, "rb")
        self._next_entry = self._read_one()

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
        return self._next_entry[0] < other._next_entry[0] or self._next_entry[1][0][0] < other._next_entry[1][0][0]


def blocks_iterator(block_names: List[str]) -> Generator[TermPostingsEntry, None, None]:
    block_files = [BlockFile(block_name) for block_name in block_names]
    heapq.heapify(block_files)

    while len(block_files) != 0:
        block_file = heapq.heappop(block_files)
        entry = block_file.read()

        if not block_file.eof():
            heapq.heappush(block_files, block_file)
        else:
            block_file.close()

        yield entry
