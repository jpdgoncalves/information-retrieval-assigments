'''
For starters I will need the following Components

Document Reader: (done for now)
- It will take a single compressed file.
- This file is a tsv which has various fields. The ones we are interested
in are "review_headline" and "review_body" fields and the "review_id" as document
identifier.
- We will use the following dataclass for now:

@dataclass
class CostumerReview:
    review_id: str
    product_title: str
    review_headline: str
    review_body: str

    @property
    def content(self):
        return f"{self.product_title} {self.review_headline} {self.review_body}"


Document Processor:
- This will split each document into tokens;
- It should return the tokens grouped by document as this is will make it much easier to calculate certain
statistics;
- It should accept accept filter functions to be used in the processing;
- The filters currently asked for this assigment are: minimum length, stopwords and stemmer;
- Processed Document and Token dataclass.

# 144724 Documents
# 74613 Terms (word with letters or numbers, that are larger than 3 characters)
'''
from time import time

from corpus import CostumerReviewReader
from processor import DocumentProcessor

import filters

_processor = DocumentProcessor()
_processor.add_filter(filters.filter_tokens_by_length(3))

start = time()
for review in CostumerReviewReader("data/amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz"):
    processed_review = _processor.process(review)
end = time()

print(end - start, "s")
