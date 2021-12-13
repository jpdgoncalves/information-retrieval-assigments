from typing import List
from definitions import Term, ReviewId

from enum import Enum, auto

import os
import shutil


class IndexCreationOptions(Enum):
    IF_EXISTS_ERROR = auto()
    IF_EXISTS_OVERWRITE = auto()


def write_review_ids(review_ids_path: str, review_ids: List[ReviewId]):
    with open(review_ids_path, "a", encoding="utf-8") as review_ids_file:
        review_ids_file.writelines(review_ids)


def _create_file(path: str):
    with open(path, "w", encoding="utf-8"):
        pass


class IndexDirectory:
    def __init__(
            self,
            index_path: str,
            block_prefix: str = "block_",
            vocabulary_file_name: str = "vocabulary.txt",
            postings_file_name: str = "postings.txt"
    ):
        self.index_path = index_path
        self.block_prefix = block_prefix
        self.vocabulary_file_name = vocabulary_file_name
        self.postings_file_name = postings_file_name

        self.review_ids_path = f"{index_path}/review_ids.txt"
        self.blocks_dir_path = f"{index_path}/blocks"
        self.segments_dir_path = f"{index_path}/segments"

        self.block_paths: List[str] = []
        self.segment_paths: List[str] = []

    @property
    def block_count(self):
        return len(self.block_paths)

    @property
    def segment_count(self):
        return len(self.segment_paths)

    def create(self, option: IndexCreationOptions = IndexCreationOptions.IF_EXISTS_ERROR):
        if os.path.exists(self.index_path):
            if option is IndexCreationOptions.IF_EXISTS_ERROR:
                raise IsADirectoryError(f"""'{self.index_path}' already exists as a directory. Choose another
                path for the index, delete the existing directory or pass 
                IndexCreationOptions.IF_EXISTS_OVERWRITE on the option parameter to overwrite 
                the directory""")
            else:
                shutil.rmtree(self.index_path)

        os.mkdir(self.index_path)
        _create_file(self.review_ids_path)
        os.mkdir(self.blocks_dir_path)
        os.mkdir(self.segments_dir_path)

    def get_block_path(self):
        """
        Creates a new block path and adds it to the internal block paths list.
        :return:
        """
        block_path = f"{self.blocks_dir_path}/{self.block_prefix}_{self.block_count}.txt"
        self.block_paths.append(block_path)
        return block_path

    def get_temp_segment_paths(self):
        """
        Creates a new pair of segment paths. One for the vocabulary file and
        another for the postings file.
        :return:
        """
        temp_segment_dir = f"{self.segments_dir_path}/{self.segment_count}"
        vocabulary_path = f"{temp_segment_dir}/{self.vocabulary_file_name}"
        postings_path = f"{temp_segment_dir}/{self.postings_file_name}"

        return vocabulary_path, postings_path

    def rename_temp_segment(self, start_term: Term, end_term: Term, temp_segment_path: str):
        """
        Function to rename a temporary segment to its permanent name.
        :param start_term:
        :param end_term:
        :param temp_segment_path:
        :return:
        """
        segment_path = f"{self.segments_dir_path}/{start_term}-{end_term}"
        os.rename(temp_segment_path, segment_path)
        self.segment_paths.append(segment_path)

    def delete_blocks_dir(self):
        shutil.rmtree(self.blocks_dir_path)
        self.block_paths = []

    def index_size(self):
        total_size = os.path.getsize(self.review_ids_path)

        for segment_path in os.listdir(self.segments_dir_path):
            for file_path in os.listdir(f"{self.segments_dir_path}/{segment_path}"):
                total_size = os.path.getsize(f"{self.segments_dir_path}/{segment_path}/{file_path}")

        return total_size
