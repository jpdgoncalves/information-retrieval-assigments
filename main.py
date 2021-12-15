"""
Script that is called to run the indexer and the searcher.

Made by: José Gonçalves nº84967
"""

from arguments import get_arguments, print_arguments, IndexingFormat
from indexing import tf_idf, bm25

import utils


def main():
    _arguments = get_arguments()
    indexing_statistics = None

    print_arguments(_arguments)

    if _arguments.indexing_format == IndexingFormat.TF_IDF:
        indexing_statistics = tf_idf.create_index(_arguments)
    elif _arguments.indexing_format == IndexingFormat.BM25:
        indexing_statistics = bm25.create_index(_arguments)

    print(f"Indexing time: {utils.format_time_interval(indexing_statistics.indexing_time)}")
    print(f"Index size: {indexing_statistics.index_size_on_disk / 1024 / 1024} MB")
    print(f"Temporary Blocks Used: {indexing_statistics.blocks_used}")
    print(f"Term Count: {indexing_statistics.term_count}")


# load_end_time = time.time()
# fmt_load_time = time.strftime('%M:%S', time.gmtime(load_end_time - load_start_time))
# print(f"[LOG]: Finished loading index. Took {fmt_load_time}.")

if __name__ == "__main__":
    main()
