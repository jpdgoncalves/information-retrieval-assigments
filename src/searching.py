from typing import List, Set, Dict
from collections import defaultdict

from definitions import (
    Segment, StemmerFunction, IndexingFormat
)
import processor
from store.postings import read_postings
from store.reviews import review_id_reader
from store.vocabulary import tf_idf_metadata_reader, bm25_metadata_reader


def get_searcher(
        idx_format: IndexingFormat,
        min_token_length: int,
        stopwords: Set[str],
        stemmer: StemmerFunction,
        segments: List[Segment],
        review_ids_path: str
):
    if idx_format is IndexingFormat.TF_IDF:
        return tf_idf_searcher(min_token_length, stopwords, stemmer, segments, review_ids_path)
    else:
        return bm25_searcher(min_token_length, stopwords, stemmer, segments, review_ids_path)


def tf_idf_searcher(
        min_token_length: int,
        stopwords: Set[str],
        stemmer: StemmerFunction,
        segments: List[Segment],
        review_ids_path: str
):
    process_query = processor.query_processor(min_token_length, stopwords, stemmer)
    read_tf_idf_meta = tf_idf_metadata_reader(segments)
    retrieve_review_ids = _review_ids_retriever(review_ids_path)

    def search(query: str, results_limit=100):
        _, term_index = process_query(query)
        terms_metadata = {}
        scores: Dict[int, float] = defaultdict(float)

        for term in term_index:
            term_metadata = read_tf_idf_meta(term)
            if term_metadata is not None:
                terms_metadata[term] = term_metadata

        term_weights = processor.normalized_tf_idf_term_index(
            term_index,
            {term: idf for term, (_, idf, _, _) in terms_metadata.items()}
        )

        for term, (term_weight, _) in term_weights.items():
            segment_path, _, offset, post_len = terms_metadata[term]
            postings = read_postings(segment_path, offset, post_len)

            for doc_id, doc_weight, _ in postings:
                scores[doc_id] += term_weight * doc_weight

        return retrieve_review_ids(scores, results_limit)

    return search


def bm25_searcher(
        min_token_length: int,
        stopwords: Set[str],
        stemmer: StemmerFunction,
        segments: List[Segment],
        review_ids_path: str
):
    process_query = processor.query_processor(min_token_length, stopwords, stemmer)
    read_bm25_meta = bm25_metadata_reader(segments)
    retrieve_review_ids = _review_ids_retriever(review_ids_path)

    def search(query: str, results_limit=100):
        _, term_index = process_query(query)
        terms_metadata = {}
        scores: Dict[int, float] = defaultdict(float)

        for term in term_index:
            term_metadata = read_bm25_meta(term)
            if term_metadata is not None:
                terms_metadata[term] = term_metadata

        for term, (segment_path, offset, post_len) in terms_metadata.items():
            postings = read_postings(segment_path, offset, post_len)

            for doc_id, doc_weight, _ in postings:
                scores[doc_id] += doc_weight

        return retrieve_review_ids(scores, results_limit)

    return search


def _review_ids_retriever(review_ids_path: str):
    read_review_id = review_id_reader(review_ids_path)

    def _retrieve_with_scores(scores: Dict[int, float], results_limit: int):
        sorted_doc_ids = sorted(
            ((score, doc_id) for doc_id, score in scores.items()),
            reverse=True
        )
        sorted_doc_ids = sorted_doc_ids if results_limit < 1 else sorted_doc_ids[:results_limit]

        with open(review_ids_path, "rb") as review_ids_file:
            search_results = [(read_review_id(review_ids_file, doc_id), score) for score, doc_id in sorted_doc_ids]

        return search_results

    return _retrieve_with_scores
