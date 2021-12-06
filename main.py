"""
Script that is called to run the indexer and the searcher.

Made by: José Gonçalves nº84967
"""
import logging
import time

from arguments import get_arguments, print_arguments, IndexingFormat
from indexer import SpimiIndexer
from processor import DocumentProcessor
from corpus import CostumerReviewReader
from index import IndexSearcher
from indexing import tf_idf, bm25

import filters


def main_refactor():
    _arguments = get_arguments()
    indexing_statistics = None

    print_arguments(_arguments)

    if _arguments.indexing_format == IndexingFormat.TF_IDF:
        indexing_statistics = tf_idf.create_index(_arguments)
    elif _arguments.indexing_format == IndexingFormat.BM25:
        indexing_statistics = bm25.create_index(_arguments)


# TODO: Use generated ids instead of the review ids.
# When constructing the index write at the end the review ids
# Their positions will be used as ids in the index
# Two passes for BM25
# Make an intermidiate index involving N, df, dl, avdl
def main():
    _arguments = get_arguments()
    _reader = CostumerReviewReader(_arguments.corpus_path)
    _processor = DocumentProcessor()
    _indexer = SpimiIndexer(_arguments.index_path, _arguments.memory_threshold)

    if _arguments.stopwords is not None:
        _processor.add_filter(
            filters.filter_stopwords(_arguments.stopwords)
        )

    if _arguments.use_potter_stemmer:
        _processor.add_filter(
            filters.stemmer("english")
        )

    _processor.add_filter(
        filters.filter_tokens_by_length(_arguments.min_token_length)
    )

    if _arguments.debug_mode:
        logging.basicConfig(level=logging.DEBUG)

    print_arguments(_arguments)
    index_start_time = time.time()

    for review in _reader:
        processed_review = _processor.process(review)
        _indexer.add_review(processed_review)

    exit(0)
    _indexer.create_index_file()

    index_end_time = time.time()
    formatted_time = time.strftime('%H:%M:%S', time.gmtime(index_end_time - index_start_time))

    print(f"[LOG]: Time for indexing: {formatted_time}s")
    print(f"[LOG]: Index size on disk: {_indexer.f_index_disk_size}")
    print(f"[LOG]: Number of terms: {_indexer.term_count}")
    print(f"[LOG]: Number of temporary segments used: {_indexer.blocks_used}")

    print(f"[LOG]: Loading index '{_indexer.index_path}'")
    load_start_time = time.time()

    searcher = IndexSearcher(_indexer.index_path)

    load_end_time = time.time()
    fmt_load_time = time.strftime('%M:%S', time.gmtime(load_end_time - load_start_time))
    print(f"[LOG]: Finished loading index. Took {fmt_load_time}.")

    query_term = input("Type a term to search (Press Enter without any input to exit): ")

    while len(query_term) > 0:
        document_frequency = searcher.search_query(query_term)
        print(f"{document_frequency} documents have the term {query_term}")
        query_term = input("Type a term to search (Press Enter without any input to exit): ")


if __name__ == "__main__":
    main_refactor()
