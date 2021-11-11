from typing import List, DefaultDict, TextIO, Optional

import heapq

from functools import total_ordering

from dictionary import PostingsDictionary


@total_ordering
class BlockFile:
    def __init__(self, block_name: str):
        self.file = open(block_name, encoding="utf-8")
        self.line = self.file.readline()
        self.term: Optional[str] = None
        self.postings: Optional[str] = None

        self.next()

    def next(self):
        """
        Sets the next term and postings of the block file.
        If the end of the file has been reached it sets them to
        None
        """
        if not self.has_next():
            self.term = None
            self.postings = None
            return

        (term, postings) = self.line.split(";", 1)
        self.term = term
        self.postings = postings
        self.line = self.file.readline()

    def has_next(self):
        """
        Tells whether there is a next term for this block file or not
        """
        return len(self.line) == 0

    def close(self):
        self.file.close()

    def __eq__(self, other):
        return self.term == other.term and self.postings == other.postings

    def __lt__(self, other):
        return (self.term, self.postings) < (other.term, other.postings)


class MergedIndex:
    def __init__(self, index_name):
        self.file = open(index_name, mode="w", encoding="utf-8")
        self.recent_term = None

    def write(self, term: str, postings: str):
        """
        Writes a postings to disk. If the term passed is the same as the previous
        one it will write on the same line otherwise it will write a newline
        :param term:
        :param postings:
        :return:
        """
        if self.recent_term is None:
            self.file.write(term)
            self.recent_term = term

        if self.recent_term != term:
            self.file.write(f"\n{term}")
            self.recent_term = term

        self.file.write(f";{postings}")

    def close(self):
        self.file.close()


def block_writer(block_name_prefix: str):
    counter = 0

    def write(postings_dictionary: PostingsDictionary):
        nonlocal counter
        block_name = f"{block_name_prefix}_{counter}.txt"
        write_block(block_name, postings_dictionary)
        counter += 1
        return block_name

    return write


def write_block(block_name: str, postings_dictionary: PostingsDictionary):

    def write_postings(postings: DefaultDict[str, List[int]], out_file: TextIO):
        for review_id in postings:
            positions = ",".join(str(pos) for pos in postings[review_id])

            out_file.write(";")
            out_file.write(review_id)
            out_file.write(positions)

        out_file.write("\n")

    with open(block_name, mode="w", encoding="utf-8") as block_file:
        postings_list = postings_dictionary.postings_list
        ordered_terms_list = sorted(
            postings_list,
            key=lambda _term: _term
        )
        
        for term in ordered_terms_list:
            block_file.write(term)
            block_file.write(";")
            write_postings(postings_list[term], block_file)


def merge_blocks(merged_file_name: str, block_file_names: List[str]):
    """
    Creates a special purpose priority queue of BlockFile.
    We request one BlockFile out of the queue at a time and write the current term and postings
    to the MergedIndex. Once the queue is empty the merging is finished and we exit the algorithm
    :param merged_file_name:
    :param block_file_names:
    :return:
    """
    merged_index = MergedIndex(merged_file_name)
    block_files = [BlockFile(block_name) for block_name in block_file_names]
    heapq.heapify(block_files)

    while len(block_files) > 0:
        block_file = heapq.heappop(block_files)
        merged_index.write(block_file.term, block_file.postings)

        if block_file.has_next():
            block_file.next()
            heapq.heappush(block_files, block_file)
        else:
            block_file.close()

    merged_index.close()
