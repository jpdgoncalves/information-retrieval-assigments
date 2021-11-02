from typing import List


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


def merge_blocks(block_file_names: List[str]):
    """
    Creates a special purpose priority queue of BlockFile.
    We request one BlockFile out of the queue at a time and write the current term and postings
    to the MergedIndex. Once the queue is empty the merging is finished and we exit the algorithm
    :param block_file_names:
    :return:
    """
    pass
