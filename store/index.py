from typing import Callable, List
from definitions import ReviewId

from enum import Enum, auto

import os
import shutil

from .blocks import BlockWriter
from .segments import IndexSegmentsWriter


class IndexCreationOptions(Enum):
    IF_EXISTS_ERROR = auto()
    IF_EXISTS_OVERWRITE = auto()


def _create_file(path: str):
    with open(path, "w", encoding="utf-8"):
        pass


class IndexDirectory:
    def __init__(
            self,
            index_path: str,
            block_prefix: str = "block_"
    ):
        self.index_path = index_path
        self.block_prefix = block_prefix
        self.review_ids_path = f"{index_path}/review_ids.txt"
        self.blocks_dir_path = f"{index_path}/blocks/"
        self.segments_dir_path = f"{index_path}/segments/"

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

    def block_writer(self):
        if not os.path.isdir(self.blocks_dir_path):
            raise NotADirectoryError(f"'{self.blocks_dir_path}' is not a directory")

        return BlockWriter(self.blocks_dir_path, self.block_prefix)

    def segments_writer(self, segment_format: Callable):
        return IndexSegmentsWriter(
            self.segments_dir_path,
            segment_format
        )

    def write_review_ids(self, review_ids: List[ReviewId]):
        with open(self.review_ids_path, "w", encoding="utf-8") as review_ids_file:
            review_ids_file.writelines(review_ids)

    def delete_blocks_dir(self):
        shutil.rmtree(self.blocks_dir_path)

    def index_size(self):
        total_size = os.path.getsize(self.review_ids_path)

        for segment_path in os.listdir(self.segments_dir_path):
            for file_path in os.listdir(f"{self.segments_dir_path}/{segment_path}"):
                total_size = os.path.getsize(f"{self.segments_dir_path}/{segment_path}/{file_path}")

        return total_size
