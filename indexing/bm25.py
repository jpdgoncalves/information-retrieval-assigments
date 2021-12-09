from definitions import IndexingStatistics

import gc
import statistics

from arguments import Arguments
from corpus import CostumerReviewReader
from dictionary import term_count_dictionary
from processor import DocumentProcessor
from store import segments
from store.index import IndexDirectory, IndexCreationOptions

import filters
import utils


def create_index(_arguments: Arguments) -> IndexingStatistics:
    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = DocumentProcessor()
    postings_dictionary = term_count_dictionary()
    memory_checker = utils.MemoryChecker(_arguments.memory_threshold)
    index_directory = IndexDirectory(_arguments.index_path)

    if _arguments.debug_mode:
        index_directory.create(IndexCreationOptions.IF_EXISTS_OVERWRITE)
    else:
        index_directory.create()

    block_writer = index_directory.block_writer()
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

    for review in review_reader:
        processed_review = review_processor.process(review)
        document_lengths.append(processed_review.document_length)

        if memory_checker.has_reached_threshold():
            block_writer.write(postings_dictionary.postings_list)
            index_directory.write_review_ids(postings_dictionary.review_ids)
            postings_dictionary = term_count_dictionary()
            gc.collect()

    block_writer.write(postings_dictionary.postings_list)
    index_directory.write_review_ids(postings_dictionary.review_ids)
    postings_dictionary = None
    gc.collect()

    avg_document_length = statistics.mean(document_lengths)
    document_count = len(document_lengths)
