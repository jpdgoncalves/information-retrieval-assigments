from definitions import IndexingStatistics

import gc
import statistics
import time

from arguments import Arguments
from corpus import CostumerReviewReader
from dictionary import term_count_dictionary
from processor import DocumentProcessor
from store import segments
from store import blocks
from store import index

import filters
import utils


def create_index(_arguments: Arguments) -> IndexingStatistics:
    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = DocumentProcessor()
    postings_dictionary = term_count_dictionary()
    memory_checker = utils.MemoryChecker(_arguments.memory_threshold)
    index_directory = index.IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    document_lengths = []

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
    segment_writer = index_directory.segments_writer(segment_format)

    for entry in blocks.blocks_iterator(index_directory.block_paths):
        segment_writer.write(entry)

    segment_writer.close()

    if not _arguments.debug_mode:
        index_directory.delete_blocks_dir()

    index_end_time = time.time()

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_directory.index_size(),
        segment_writer.term_count,
        index_directory.block_count
    )