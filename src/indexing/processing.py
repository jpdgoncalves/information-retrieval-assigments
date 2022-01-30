"""
Module containing utility functions used during the indexing pipeline.
"""
import gc
import statistics

from src import processor
from src.arguments import Arguments
from src.store.segments import BufferedSegmentWriter
from src.definitions import SegmentFormat, Processor, RawReviewReader
from src.dictionary import PostingsDictionary
from src.store import blocks, segments
from src.store.blocks import blocks_iterator
from src.store.index import IndexDirectory
from src.utils import MemoryChecker


def tf_idf_review_processor(_arguments: Arguments):
    stemmer = processor.english_stemmer if _arguments.use_potter_stemmer else processor.no_stemmer
    return processor.review_processor(
        _arguments.min_token_length,
        _arguments.stopwords,
        stemmer,
        processor.normalized_tf_term_index
    )


def bm_25_review_processor(_arguments: Arguments):
    stemmer = processor.english_stemmer if _arguments.use_potter_stemmer else processor.no_stemmer
    return processor.review_processor(
        _arguments.min_token_length,
        _arguments.stopwords,
        stemmer,
        processor.count_term_index
    )


def index_reviews(
        review_reader: RawReviewReader,
        review_processor: Processor,
        index_directory: IndexDirectory,
        memory_checker: MemoryChecker
):
    """
    Utility function that contains the logic for indexing the reviews
    into blocks using the SPIMI algorithm.
    :param review_reader:
    :param review_processor:
    :param index_directory:
    :param memory_checker:
    :return:
    """
    print("[processing]: Indexing reviews into blocks.")
    postings_dictionary = PostingsDictionary()
    document_lengths = []

    for review in review_reader:
        processed_review = review_processor(review)
        _, _, _, document_length = processed_review
        postings_dictionary.add_document(processed_review)
        document_lengths.append(document_length)

        if memory_checker.has_reached_threshold():
            blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
            src.store.reviews.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
            postings_dictionary = PostingsDictionary()
            collect_garbage()

    blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
    src.store.reviews.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
    postings_dictionary = None
    collect_garbage()

    print("[processing]: Done indexing.")
    return document_lengths


def merge_tf_idf_blocks(document_lengths: list[int], index_dir: IndexDirectory, _arguments: Arguments):
    review_count = len(document_lengths)
    segment_format = segments.tf_idf_format(review_count)

    term_count = merge_blocks(index_dir, segment_format, _arguments.debug_mode)
    index_size = index_dir.index_size()

    return review_count, term_count, index_size


def merge_bm25_blocks(document_lengths: list[int], index_dir: IndexDirectory, _arguments: Arguments):
    avg_document_length = statistics.mean(document_lengths)
    review_count = len(document_lengths)

    segment_format = segments.bm25_format(
        review_count,
        avg_document_length,
        document_lengths,
        _arguments.b,
        _arguments.k1
    )

    term_count = merge_blocks(index_dir, segment_format, _arguments.debug_mode)
    index_size = index_dir.index_size()

    return review_count, term_count, index_size


def merge_blocks(index_directory: IndexDirectory, segment_format: SegmentFormat, debug_mode: bool):
    """
    Utility function that merges the block files into the final index.
    :param index_directory:
    :param segment_format:
    :param debug_mode
    :return:
    """
    print("[processing]: Merging blocks into final index")
    segment_writer = BufferedSegmentWriter(segment_format, index_directory)

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
