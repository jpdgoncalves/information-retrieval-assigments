"""
Module containing the function that creates the Corpus Reader.
"""

import csv
import gzip
from collections import defaultdict

from definitions import RawReviewReader

# Required because the fields we are reading very large fields.
csv.field_size_limit(csv.field_size_limit() * 2)


def raw_review_reader(review_file_path: str, doc_id_counter: int = 0) -> RawReviewReader:
    """
    Creates a Generator for the corpus file specified by the path parameter that
    creates instances of CostumerReview. Optionally a doc_id_counter maybe given
    to the generator for it to start from a non-zero id.
    """
    with gzip.open(review_file_path, "rt", encoding="utf-8") as review_file:
        tsv_reader = csv.DictReader(review_file, delimiter="\t")

        for review_row in tsv_reader:
            review = defaultdict(str, review_row)

            yield (
                doc_id_counter,
                review["review_id"],
                f"{review['product_title']} {review['review_headline']} {review['review_body']}"
            )

            doc_id_counter += 1
