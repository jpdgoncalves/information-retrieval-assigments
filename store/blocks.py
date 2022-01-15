from typing import List, Generator, TextIO, Optional
from definitions import Vocabulary, TermPostingsEntry
from .postings import serialize_postings, deserialize_postings

import heapq
# import pickle

# def write_block(block_path: str, vocabulary: Vocabulary):
#     with open(block_path, "wb", buffering=1024 * 1024) as block_file:
#         print(f"[BlockWriter]: Writing {block_path}")
#
#         sorted_terms = sorted(vocabulary.keys())
#
#         for term in sorted_terms:
#             pickle.dump((term, vocabulary[term]), block_file, pickle.HIGHEST_PROTOCOL)
#
#         print(f"[BlockWriter]: Finished writing {block_path}")


def write_block(block_path: str, vocabulary: Vocabulary):

    with open(block_path, "w", newline="\n") as block_file:
        print(f"[BlockWriter]: Writing {block_path}")

        sorted_terms = sorted(vocabulary.keys())

        for term in sorted_terms:
            block_file.write(f"{term};{serialize_postings(vocabulary[term])}\n")

        print(f"[BlockWriter]: Finished writing {block_path}")


# class BlockFile:
#
#     def __init__(self, block_path: str):
#         self.block_path = block_path
#         self.block_file = open(block_path, "rb")
#         self._next_entry: TermPostingsEntry = self._read_one()
#
#     def _read_one(self) -> Optional[TermPostingsEntry]:
#         try:
#             return pickle.load(self.block_file)
#         except EOFError:
#             return None
#
#     def read(self) -> Optional[TermPostingsEntry]:
#         entry = self._next_entry
#         self._next_entry = self._read_one()
#
#         return entry
#
#     def eof(self):
#         return self._next_entry is None
#
#     def close(self):
#         self.block_file.close()
#
#     # noinspection PyProtectedMember
#     def __lt__(self, other):
#         this_term = self._next_entry[0]
#         other_term = other._next_entry[0]
#         this_first_doc_id = self._next_entry[1][0][0]
#         other_first_doc_id = other._next_entry[1][0][0]
#
#         return (this_term, this_first_doc_id) < (other_term, other_first_doc_id)
#
#     def __repr__(self):
#         return f"{self._next_entry[0]}"
#
#
# def blocks_iterator(block_paths: List[str]) -> Generator[TermPostingsEntry, None, None]:
#     block_files = [BlockFile(block_path) for block_path in block_paths]
#     heapq.heapify(block_files)
#
#     while len(block_files) != 0:
#         # print(block_files)
#         block_file = heapq.heappop(block_files)
#         entry = block_file.read()
#
#         if not block_file.eof():
#             heapq.heappush(block_files, block_file)
#         else:
#             block_file.close()
#
#         yield entry


def block(block_path: Optional[str] = None, *, f: Optional[TextIO] = None):
    block_file = f if block_path is None else open(block_path)
    block_line = block_file.readline()

    if len(block_line) == 0:
        block_file.close()
        return None

    term, posting_data = block_line.split(";", 1)
    postings = deserialize_postings(posting_data)
    return term, postings[0][0], postings, block_file


def blocks_iterator(block_paths: List[str]) -> Generator[TermPostingsEntry, None, None]:

    blocks = [block(block_path) for block_path in block_paths]
    heapq.heapify(blocks)

    while len(blocks) != 0:
        top_block = heapq.heappop(blocks)
        term, _, postings, block_file = top_block

        yield term, postings

        new_block = block(f=block_file)

        if new_block is not None:
            heapq.heappush(blocks, new_block)
