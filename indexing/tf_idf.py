import time

import processor
from arguments import Arguments
from corpus import raw_review_reader
from definitions import IndexingStatistics
from store import segments, index, idxprops
from utils import MemoryChecker
from .processing import merge_blocks, index_reviews


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = raw_review_reader(_arguments.corpus_path)
    stemmer = processor.english_stemmer if _arguments.use_potter_stemmer else processor.no_stemmer
    review_processor = processor.review_processor(
        _arguments.min_token_length,
        _arguments.stopwords,
        stemmer,
        processor.normalized_tf_term_index
    )
    memory_checker = MemoryChecker(_arguments.memory_threshold)
    index_directory = index.IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    index_start_time = time.time()

    document_lengths = index_reviews(
        review_reader, review_processor,
        index_directory, memory_checker
    )
    review_count = len(document_lengths)
    segment_format = segments.tf_idf_format(review_count)

    term_count = merge_blocks(index_directory, segment_format, _arguments.debug_mode)
    index_size = index_directory.index_size()

    index_end_time = time.time()

    idxprops.write_props(
        index_directory.idx_props_path,
        _arguments.indexing_format,
        index_size,
        term_count,
        review_count,
        _arguments.min_token_length,
        _arguments.stopwords,
        stemmer
    )

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_size,
        term_count,
        review_count,
        index_directory.block_count
    )
