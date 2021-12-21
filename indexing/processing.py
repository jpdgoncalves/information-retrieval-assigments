"""
Module containing utility functions used during the indexing pipeline.
"""
import gc
from typing import Callable

from definitions import SegmentWriteFormat, Processor, RawReviewReader
from dictionary import PostingsDictionary
from store import blocks, index
from store.blocks import blocks_iterator
from store.index import IndexDirectory
from utils import MemoryChecker
from .segments import SegmentWriter


def index_reviews(
        review_reader: RawReviewReader,
        review_processor: Processor,
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
    print("[processing]: Indexing reviews into blocks.")
    postings_dictionary = dictionary_constructor()
    document_lengths = []

    for review in review_reader:
        processed_review = review_processor(review)
        _, _, _, document_length = processed_review
        postings_dictionary.add_document(processed_review)
        document_lengths.append(document_length)

        if memory_checker.has_reached_threshold():
            blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
            index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
            postings_dictionary = dictionary_constructor()
            collect_garbage()

    blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
    index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
    postings_dictionary = None
    collect_garbage()

    print("[processing]: Done indexing.")
    return document_lengths


def merge_blocks(index_directory: IndexDirectory, segment_format: SegmentWriteFormat, debug_mode: bool):
    """
    Utility function that merges the block files into the final index.
    :param index_directory:
    :param segment_format:
    :param debug_mode
    :return:
    """
    print("[processing]: Merging blocks into final index")
    segment_writer = SegmentWriter(index_directory, segment_format)

    for entry in blocks_iterator(index_directory.block_paths):
        segment_writer.write(entry)

    segment_writer.flush()

    if not debug_mode:
        index_directory.delete_blocks_dir()

    print("[processing]: Done merging.")
    return segment_writer.term_count


def collect_garbage():
    print("[processing]: Collecting garbage")
    gc.collect()
    print("[processing]: Finished collecting garbage")
