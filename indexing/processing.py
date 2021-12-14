from arguments import Arguments
from processor import ReviewProcessor
import filters


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
