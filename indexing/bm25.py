from definitions import IndexingStatistics

from arguments import Arguments
from corpus import CostumerReviewReader
from processor import DocumentProcessor

import filters


def create_index(_arguments: Arguments) -> IndexingStatistics:
    review_reader = CostumerReviewReader(_arguments.corpus_path)
    review_processor = DocumentProcessor()

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
