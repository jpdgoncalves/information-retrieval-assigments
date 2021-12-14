import time

from arguments import Arguments
from corpus import CostumerReviewReader
from definitions import IndexingStatistics
from dictionary import tf_idf_dictionary
from store import segments, index
from utils import MemoryChecker
from .processing import get_review_processor, merge_blocks, index_reviews


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = get_review_processor(_arguments)
    memory_checker = MemoryChecker(_arguments.memory_threshold)
    index_directory = index.IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    index_start_time = time.time()

    document_lengths = index_reviews(
        review_reader, review_processor, tf_idf_dictionary,
        index_directory, memory_checker
    )
    review_count = len(document_lengths)
    segment_format = segments.tf_idf_format(review_count)

    term_count = merge_blocks(index_directory, segment_format, _arguments)

    index_end_time = time.time()

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_directory.index_size(),
        term_count,
        index_directory.block_count
    )
