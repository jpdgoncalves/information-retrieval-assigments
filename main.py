from arguments import get_arguments
from indexer import SpimiIndexer
from processor import DocumentProcessor
from reader import CostumerReviewReader

import filters


def main():
    _arguments = get_arguments()
    _reader = CostumerReviewReader(_arguments.corpus_path)
    _processor = DocumentProcessor()
    _indexer = SpimiIndexer(_arguments.index_path, _arguments.memory_threshold)

    _processor.add_filter(
        filters.filter_token(
            lambda token: len(token.word) >= _arguments.min_token_length
        )
    )

    if _arguments.stopwords is not None:
        _processor.add_filter(
            filters.filter_token(
                lambda token: token.word not in _arguments.stopwords
            )
        )

    if _arguments.use_potter_stemmer:
        _processor.add_filter(
            filters.stemmer("english")
        )

    for review in _reader:
        processed_review = _processor.process(review)
        _indexer.add_review(processed_review)

    _indexer.create_index_file()


if __name__ == "__main__":
    main()
