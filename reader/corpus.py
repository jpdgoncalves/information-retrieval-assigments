"""
Module containing the function that creates the Corpus Reader.
"""
from dataclasses import dataclass

import csv
import gzip

# Required because the fields we are reading very large fields.
csv.field_size_limit(csv.field_size_limit() * 2)


@dataclass
class CostumerReview:
    review_id: str
    product_title: str
    review_headline: str
    review_body: str

    @property
    def content(self):
        return f"{self.product_title} {self.review_headline} {self.review_body}"


def CostumerReviewReader(review_file_path: str):
    """
    Creates a Generator for the corpus file specified by the path parameter that
    creates instances of CostumerReview.
    """
    with gzip.open(review_file_path, "rt", encoding="utf-8") as review_file:
        tsv_reader = csv.DictReader(review_file, delimiter="\t")

        for review_row in tsv_reader:
            yield CostumerReview(
                review_row["review_id"],
                review_row["product_title"].lower(),
                review_row["review_headline"].lower(),
                review_row["review_body"].lower()
            )
