import gc
import statistics
import time

import utils
from arguments import Arguments
from corpus import CostumerReviewReader
from definitions import IndexingStatistics
from dictionary import term_count_dictionary
from store import segments, index, blocks
from .processing import get_review_processor, merge_blocks


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = get_review_processor(_arguments)
    postings_dictionary = term_count_dictionary()
    memory_checker = utils.MemoryChecker(_arguments.memory_threshold)
    index_directory = index.IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    document_lengths = []

    index_start_time = time.time()

    for review in review_reader:
        processed_review = review_processor.process(review)
        postings_dictionary.add_document(processed_review)
        document_lengths.append(processed_review.document_length)

        if memory_checker.has_reached_threshold():
            blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
            index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
            postings_dictionary = term_count_dictionary()
            gc.collect()

    blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
    index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
    postings_dictionary = None
    gc.collect()

    avg_document_length = statistics.mean(document_lengths)
    document_count = len(document_lengths)

    segment_format = segments.bm25_format(
        document_count,
        avg_document_length,
        document_lengths,
        _arguments.b,
        _arguments.k1
    )

    term_count = merge_blocks(index_directory, segment_format, _arguments)

    index_end_time = time.time()

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_directory.index_size(),
        term_count,
        index_directory.block_count
    )
