import time

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

    index_start_time = time.time()

    for review in _reader:
        processed_review = _processor.process(review)
        _indexer.add_review(processed_review)

    _indexer.create_index_file()

    index_end_time = time.time()
    formated_time = time.strftime('%M:%S', time.gmtime(index_end_time - index_start_time))

    print(f"[LOG]: Time for indexing: {formated_time}s")
    print(f"[LOG]: Index size on disk: {_indexer.f_index_disk_size}")
    print(f"[LOG]: Number of terms: {_indexer.term_count}")
    print(f"[LOG]: Number of temporary segments used: {_indexer.blocks_used}")


if __name__ == "__main__":
    main()
