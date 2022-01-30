import time

from src.arguments import Arguments
from src.corpus import raw_review_reader
from src.definitions import IndexingStatistics, IndexingFormat
from src.indexing.processing import bm_25_review_processor, index_reviews, merge_bm25_blocks, tf_idf_review_processor, \
    merge_tf_idf_blocks
from src.store import idxprops, index
from src.store.index import IndexDirectory
from src.utils import MemoryChecker


def get_processor(_arguments: Arguments):
    if _arguments.indexing_format == IndexingFormat.TF_IDF:
        return tf_idf_review_processor(_arguments)
    else:
        return bm_25_review_processor(_arguments)


def merge_blocks(document_lengths: list[int], index_dir: IndexDirectory, _arguments: Arguments):
    if _arguments.indexing_format == IndexingFormat.TF_IDF:
        return merge_tf_idf_blocks(document_lengths, index_dir, _arguments)
    else:
        return merge_bm25_blocks(document_lengths, index_dir, _arguments)


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = raw_review_reader(_arguments.corpus_path)
    review_processor = get_processor(_arguments)
    memory_checker = MemoryChecker(_arguments.memory_threshold)
    index_directory = IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    index_start_time = time.time()

    document_lengths = index_reviews(review_reader, review_processor, index_directory, memory_checker)
    review_count, term_count, index_size = merge_blocks(document_lengths, index_directory, _arguments)

    idxprops.write_props(
        index_directory.idx_props_path, _arguments.indexing_format,
        index_size, term_count, review_count,
        _arguments.min_token_length, _arguments.stopwords,
        _arguments.use_potter_stemmer
    )

    index_end_time = time.time()

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_size,
        term_count,
        review_count,
        index_directory.block_count
    )
