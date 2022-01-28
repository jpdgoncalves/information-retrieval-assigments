import time

import utils
from arguments import Arguments
from corpus import raw_review_reader
from definitions import IndexingStatistics
from store import index, idxprops
from .processing import bm_25_review_processor, merge_bm25_blocks, index_reviews


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = raw_review_reader(_arguments.corpus_path)
    review_processor = bm_25_review_processor(_arguments)
    memory_checker = utils.MemoryChecker(_arguments.memory_threshold)
    index_directory = index.IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    index_start_time = time.time()

    document_lengths = index_reviews(review_reader, review_processor, index_directory, memory_checker)
    review_count, term_count, index_size = merge_bm25_blocks(document_lengths, index_directory, _arguments)

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
