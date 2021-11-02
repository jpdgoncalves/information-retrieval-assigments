from typing import List, DefaultDict, TextIO

from dictionary import PostingsDictionary


class BlockFile:
    def __init__(self):
        self.file = None
        self.term = None
        self.postings = None

    def next(self):
        """
        Reads the next line of the block file if there is one
        :return:
        """
        pass

    def has_next(self):
        """
        Checks if there is a next line to read from the block file
        :return:
        """


class MergedIndex:
    def __init__(self):
        self.file = None
        self.recent_term = None

    def write(self, term, postings):
        """
        Writes a postings to disk. If the term passed is the same as the previous
        one it will write on the same line otherwise it will write a newline
        :param term:
        :param postings:
        :return:
        """
        pass

    def close(self):
        pass


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

    with open(block_name, encoding="utf-8") as block_file:
        postings_list = postings_dictionary.postings_list
        for term in postings_list:
            block_file.write(term)
            block_file.write(";")
            write_postings(postings_list[term], block_file)


def merge_blocks(merged_file_name: str, block_file_names: List[str]):
    """
    Creates a special purpose priority queue of BlockFile.
    We request one BlockFile out of the queue at a time and write the current term and postings
    to the MergedIndex. Once the queue is empty the merging is finished and we exit the algorithm
    :param block_file_names:
    :return:
    """
    pass
