from enum import Enum, auto

import os
import shutil

from .blocks import BlockWriter


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
            block_prefix: str = "block_",
            segment_prefix: str = "segment_",
            vocab_name: str = "vocabulary.txt",
            postings_name: str = "postings.txt"
    ):
        self.index_path = index_path
        self.block_prefix = block_prefix
        self.segment_prefix = segment_prefix
        self.vocab_name = vocab_name
        self.postings_name = postings_name
        self.review_ids_path = f"{index_path}/review_ids.txt"
        self.review_ids_idx_path = f"{index_path}/review_ids_idx.txt"
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
        _create_file(self.review_ids_idx_path)
        os.mkdir(self.blocks_dir_path)
        os.mkdir(self.segments_dir_path)

    def block_writer(self):
        if not os.path.isdir(self.blocks_dir_path):
            raise NotADirectoryError(f"'{self.blocks_dir_path}' is not a directory")

        return BlockWriter(self.blocks_dir_path, self.block_prefix)
