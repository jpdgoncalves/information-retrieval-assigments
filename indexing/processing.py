"""
Module containing utility functions used during the indexing pipeline
"""
import gc
from typing import Callable

import filters
from arguments import Arguments
from corpus import CostumerReviewReader
from definitions import SegmentWriteFormat
from dictionary import PostingsDictionary
from processor import ReviewProcessor
from store import blocks, index
from store.blocks import blocks_iterator
from store.index import IndexDirectory
from utils import MemoryChecker
from .segments import SegmentWriter


def get_review_processor(_arguments: Arguments):
    """
    Utility function to build the Review processor from the arguments passed to it.
    :param _arguments:
    :return:
    """
    review_processor = ReviewProcessor()

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

    return review_processor


def index_reviews(
        review_reader: CostumerReviewReader,
        review_processor: ReviewProcessor,
        dictionary_constructor: Callable[[], PostingsDictionary],
        index_directory: IndexDirectory,
        memory_checker: MemoryChecker
):
    """
    Utility function that contains the logic for indexing the reviews
    into blocks using the SPIMI algorithm.
    :param review_reader:
    :param review_processor:
    :param dictionary_constructor:
    :param index_directory:
    :param memory_checker:
    :return:
    """
    print("[processing] Indexing reviews into blocks.")
    postings_dictionary = dictionary_constructor()
    document_lengths = []

    for review in review_reader:
        processed_review = review_processor.process(review)
        postings_dictionary.add_document(processed_review)
        document_lengths.append(processed_review.document_length)

        if memory_checker.has_reached_threshold():
            blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
            index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
            postings_dictionary = dictionary_constructor()
            gc.collect()

    blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
    index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
    postings_dictionary = None
    gc.collect()

    print("[processing] Done.")
    return document_lengths


def merge_blocks(index_directory: IndexDirectory, segment_format: SegmentWriteFormat, _arguments: Arguments):
    """
    Utility function that merges the block files into the final index.
    :param index_directory:
    :param segment_format:
    :param _arguments:
    :return:
    """
    print("[processing] Merging blocks into final index")
    segment_writer = SegmentWriter(index_directory, segment_format)

    for entry in blocks_iterator(index_directory.block_paths):
        segment_writer.write(entry)

    if not _arguments.debug_mode:
        index_directory.delete_blocks_dir()

    print("[processing] Done.")
    return segment_writer.term_count
