"""
Script that is called to run the indexer and the searcher.

Made by: José Gonçalves nº84967
"""
import time

from arguments import get_arguments, print_arguments
from indexer import SpimiIndexer
from processor import DocumentProcessor
from reader.corpus import CostumerReviewReader
from reader.index import IndexSearcher

import filters


# TODO: Use generated ids instead of the review ids.
# When constructing the index write at the end the review ids
# Their positions will be used as ids in the index
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

    print_arguments(_arguments)
    index_start_time = time.time()

    for review in _reader:
        processed_review = _processor.process(review)
        _indexer.add_review(processed_review)

    _indexer.create_index_file()

    index_end_time = time.time()
    formatted_time = time.strftime('%M:%S', time.gmtime(index_end_time - index_start_time))

    print(f"[LOG]: Time for indexing: {formatted_time}s")
    print(f"[LOG]: Index size on disk: {_indexer.f_index_disk_size}")
    print(f"[LOG]: Number of terms: {_indexer.term_count}")
    print(f"[LOG]: Number of temporary segments used: {_indexer.blocks_used}")

    print(f"[LOG]: Loading index '{_indexer.index_name}'")
    load_start_time = time.time()

    searcher = IndexSearcher(_indexer.index_name)

    load_end_time = time.time()
    fmt_load_time = time.strftime('%M:%S', time.gmtime(load_end_time - load_start_time))
    print(f"[LOG]: Finished loading index. Took {fmt_load_time}.")

    query_term = input("Type a term to search (Press Enter without any input to exit): ")

    while len(query_term) > 0:
        document_frequency = searcher.search_query(query_term)
        print(f"{document_frequency} documents have the term {query_term}")
        query_term = input("Type a term to search (Press Enter without any input to exit): ")

if __name__ == "__main__":
    main()
