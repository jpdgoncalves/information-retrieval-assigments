"""
Module containing the function that creates the Corpus Reader.
"""

import csv
import gzip

from definitions import CostumerReview

# Required because the fields we are reading very large fields.
csv.field_size_limit(csv.field_size_limit() * 2)


def CostumerReviewReader(review_file_path: str, doc_id_counter: int = 0):
    """
    Creates a Generator for the corpus file specified by the path parameter that
    creates instances of CostumerReview. Optionally a doc_id_counter maybe given
    to the generator for it to start from a non-zero id.
    """
    with gzip.open(review_file_path, "rt", encoding="utf-8") as review_file:
        tsv_reader = csv.DictReader(review_file, delimiter="\t")

        for review_row in tsv_reader:
            yield CostumerReview(
                doc_id_counter,
                review_row["review_id"],
                review_row["product_title"].lower() if review_row["review_headline"] is not None else "",
                review_row["review_headline"].lower() if review_row["review_headline"] is not None else "",
                review_row["review_body"].lower() if review_row["review_headline"] is not None else ""
            )

            doc_id_counter += 1
