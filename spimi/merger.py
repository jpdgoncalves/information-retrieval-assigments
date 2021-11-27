from typing import List

import heapq

from .blocks import BlockReader


class BlockMerger:
    def __init__(self, index_name):
        self.file = open(index_name, mode="w", encoding="utf-8")
        self.recent_term = None
        self.term_count = 0

    def write(self, term: str, postings: str):
        """
        Writes a postings to disk. If the term passed is the same as the previous
        one it will write on the same line otherwise it will write a newline
        :param term:
        :param postings:
        :return:
        """
        if self.recent_term is None:
            self.term_count += 1
            self.file.write(term)
            self.recent_term = term

        if self.recent_term != term:
            self.term_count += 1
            self.file.write(f"\n{term}")
            self.recent_term = term

        self.file.write(f";{postings}")

    def close(self):
        self.file.close()


def merge_blocks(merged_file_name: str, block_file_names: List[str]) -> int:
    """
    Creates a special purpose priority queue of BlockFile.
    We request one BlockFile out of the queue at a time and write the current term and postings
    to the MergedIndex. Once the queue is empty the merging is finished and we exit the algorithm
    :param merged_file_name:
    :param block_file_names:
    :return: Count of the number of term writen to disk.
    """
    print(f"[LOG]: Merging blocks into '{merged_file_name}'")

    merged_index = BlockMerger(merged_file_name)
    block_files = [BlockReader(block_name) for block_name in block_file_names]
    heapq.heapify(block_files)

    while len(block_files) > 0:
        block_file = heapq.heappop(block_files)

        # print(block_file)

        merged_index.write(block_file.term, block_file.postings)

        if block_file.has_next():
            block_file.next()
            heapq.heappush(block_files, block_file)
        else:
            block_file.close()

    merged_index.close()

    return merged_index.term_count
