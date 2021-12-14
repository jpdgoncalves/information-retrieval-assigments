import filters
from arguments import Arguments
from definitions import SegmentWriteFormat
from processor import ReviewProcessor
from store.blocks import blocks_iterator
from store.index import IndexDirectory
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


def merge_blocks(index_directory: IndexDirectory, segment_format: SegmentWriteFormat, _arguments: Arguments):
    segment_writer = SegmentWriter(index_directory, segment_format)

    for entry in blocks_iterator(index_directory.block_paths):
        segment_writer.write(entry)

    if not _arguments.debug_mode:
        index_directory.delete_blocks_dir()

    return segment_writer.term_count