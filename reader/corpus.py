"""
Module containing the function that creates the Corpus Reader.
"""

import csv
import gzip

# Required because the fields we are reading very large fields.
csv.field_size_limit(csv.field_size_limit() * 2)


class CostumerReview:
    def __init__(self, doc_id: int, review_id: str, product_title: str, review_headline: str, review_body: str):
        self.doc_id = doc_id
        self.review_id = review_id
        self.product_title = product_title
        self.review_headline = review_headline
        self.review_body = review_body

    @property
    def content(self):
        return f"{self.product_title} {self.review_headline} {self.review_body}"


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
