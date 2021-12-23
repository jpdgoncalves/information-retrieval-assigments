from time import time

import processor
from corpus import raw_review_reader

corpus_path = "data/amazon_reviews_us_Books_v1_00.tsv.gz"
process_review = processor.review_processor(3, set(), processor.english_stemmer)

start = time()
for raw_review in raw_review_reader(corpus_path):
    processed_review = process_review(raw_review)
end = time()

print(end - start, "s")
