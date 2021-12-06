from definitions import IndexingStatistics

import gc

from arguments import Arguments
from corpus import CostumerReviewReader
from dictionary import tf_idf_dictionary
from processor import DocumentProcessor
from utils import MemoryChecker

import filters


CALL_CONTROL = 100


def create_index(_arguments: Arguments) -> IndexingStatistics:

    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = DocumentProcessor()
    memory_checker = MemoryChecker(_arguments.memory_threshold, CALL_CONTROL)
    postings_dictionary = tf_idf_dictionary()
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

    for review in review_reader:
        processed_review = review_processor.process(review)
        postings_dictionary.add_document(processed_review)
        review_count += 1

        if memory_checker.has_reached_threshold():
            # Write review_ids to file
            # Write block to blocks folder
            pass

    # write last block
    # merge blocks into the segments folders
