import gc
import time

from arguments import Arguments
from corpus import CostumerReviewReader
from definitions import IndexingStatistics
from dictionary import tf_idf_dictionary
from store import segments, index, blocks
from utils import MemoryChecker
from .processing import get_review_processor
from .segments import SegmentWriter


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = get_review_processor(_arguments)
    memory_checker = MemoryChecker(_arguments.memory_threshold)
    postings_dictionary = tf_idf_dictionary()
    index_directory = index.IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(index.IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    review_count = 0

    index_start_time = time.time()

    for review in review_reader:
        processed_review = review_processor.process(review)
        postings_dictionary.add_document(processed_review)
        review_count += 1

        if memory_checker.has_reached_threshold():
            blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
            index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
            postings_dictionary = tf_idf_dictionary()
            gc.collect()

    blocks.write_block(index_directory.get_block_path(), postings_dictionary.postings_list)
    index.write_review_ids(index_directory.review_ids_path, postings_dictionary.review_ids)
    postings_dictionary = None
    gc.collect()

    segment_format = segments.tf_idf_format(review_count)
    segment_writer = SegmentWriter(index_directory, segment_format)

    for entry in blocks.blocks_iterator(index_directory.block_paths):
        segment_writer.write(entry)
    
    if not _arguments.debug_mode:
        index_directory.delete_blocks_dir()

    index_end_time = time.time()

    return IndexingStatistics(
        index_end_time - index_start_time,
        index_directory.index_size(),
        segment_writer.term_count,
        index_directory.block_count
    )
