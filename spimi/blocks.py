from typing import Optional, List, Dict, TextIO

from functools import total_ordering

import logging

from dictionary import PostingsDictionary


@total_ordering
class BlockReader:
    def __init__(self, block_name: str):
        self.file = open(block_name, encoding="utf-8")
        self.line = self.file.readline().strip()
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
        self.line = self.file.readline().strip()

    def has_next(self):
        """
        Tells whether there is a next term for this block file or not
        """
        return len(self.line) != 0

    def close(self):
        self.file.close()

    def __eq__(self, other):
        return self.term == other.term and self.postings == other.postings

    def __lt__(self, other):
        return (self.term, self.postings) < (other.term, other.postings)

    def __str__(self):
        return f"{self.line}, {self.term}, {self.postings}"


def _write_postings(term: str, block_file: TextIO, postings: Dict[int, List[int]]):
    """
    Writes a single line of the block file
    :param term:
    :param block_file:
    :param postings:
    :return:
    """
    block_file.write(term)

    for doc_id, positions in postings.items():
        block_file.write(f";{doc_id}:{len(positions)}:")

        first_pos, *remaining_pos = positions

        block_file.write(str(first_pos))

        for pos in remaining_pos:
            block_file.write(",")
            block_file.write(str(pos))

    block_file.write("\n")


class BlockWriter:
    """
    Class responsible for writing blocks and store information
    relevant to retrieve them.
    """
    def __init__(self, reviews_ids_path: str, blocks_dir_path: str, prefix: str):
        self.review_ids_path = reviews_ids_path
        self.blocks_dir_path = blocks_dir_path
        self.block_prefix = prefix
        self.block_names: List[str] = []

    @property
    def block_count(self):
        return len(self.block_names)

    def write_block(self, postings_dict: PostingsDictionary):
        """
        Writes a temporary block and the review ids.
        :param postings_dict:
        :return:
        """
        self._write_review_ids(postings_dict)
        block_name = self._write_block(postings_dict)
        self.block_names.append(block_name)

    def _write_review_ids(self, postings_dict: PostingsDictionary):
        """
        Writes the review ids. This is used to map doc_ids to review_ids.
        :param postings_dict:
        :return:
        """
        logging.debug(f"Writing review ids to {self.review_ids_path}")

        with open(self.review_ids_path, "a") as review_ids_file:
            for doc_id in postings_dict.doc_id_mapping:
                review_ids_file.write(postings_dict.doc_id_mapping[doc_id])
                review_ids_file.write("\n")

        logging.debug(f"Finished writing review ids to {self.review_ids_path}")

    def _write_block(self, postings_dict: PostingsDictionary):
        """
        Writes a temporary block.
        :param postings_dict:
        :return:
        """
        block_name = f"{self.blocks_dir_path}/{self.block_prefix}{self.block_count}.txt"
        postings_list = postings_dict.postings_list
        ordered_terms_list = sorted(postings_list.keys())

        logging.debug(f"Writing block to {block_name}")

        with open(block_name, "w") as block_file:

            for term in ordered_terms_list:
                _write_postings(term, block_file, postings_list[term])

        logging.debug(f"Finished writing block to {block_name}")

        return block_name
