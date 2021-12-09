from definitions import IndexingStatistics

import time
import gc

from arguments import Arguments
from corpus import CostumerReviewReader
from dictionary import tf_idf_dictionary
from processor import DocumentProcessor
from store import segments
from store.index import IndexDirectory, IndexCreationOptions
from store.blocks import blocks_iterator
from utils import MemoryChecker

import filters


CALL_CONTROL = 100


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = DocumentProcessor()
    memory_checker = MemoryChecker(_arguments.memory_threshold, CALL_CONTROL)
    postings_dictionary = tf_idf_dictionary()
    index_directory = IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    block_writer = index_directory.block_writer()
    review_count = 0

    if _arguments.stopwords is not None:
        review_processor.add_filter(
            filters.filter_stopwords(_arguments.stopwords)
        )

    if _arguments.use_potter_stemmer:
        review_processor.add_filter(
            filters.stemmer("english")
        )

    review_processor.add_filter(
        filters.filter_tokens_by_length(_arguments.min_token_length)
    )

    index_start_time = time.time()

    for review in review_reader:
        processed_review = review_processor.process(review)
        postings_dictionary.add_document(processed_review)
        review_count += 1

        if memory_checker.has_reached_threshold():
            block_writer.write(postings_dictionary.postings_list)
            postings_dictionary = tf_idf_dictionary()
            gc.collect()

    block_writer.write(postings_dictionary.postings_list)
    postings_dictionary = None
    gc.collect()

    segment_format = segments.tf_idf_format(review_count)
    segment_writer = index_directory.segments_writer(segment_format)

    for entry in blocks_iterator(block_writer.block_paths):
        segment_writer.write(entry)

    segment_writer.close()
    
    if not _arguments.debug_mode:
        index_directory.delete_blocks_dir()

    index_end_time = time.time()

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_directory.index_size(),
        segment_writer.term_count,
        block_writer.block_count
    )
