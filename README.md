# Information Retrieval Assigments

## Prepare the environment
- Create a virtual environment (Python 3.9)
- Active the virtual environment
- Install the requirements in `requirements.txt`

## Run the Code
- Activate the virtual environment if it isn't already
- Run ```python src/main.py [options]```

With this configuration the script should create an index folder
called `results/segmented_index`. The tokens will have a length equal or larger
than 3 characters, stopwords will be filtered and words will be stemmed

After the indexing process is done it will run load the index and the
queries in `data/queries.txt`. Then for each query it will retrieve
the top 100 results and write them into `results/results.txt`

## Command Options

- ``-mtl --min-token-length <length>``: Defines the minimum length the tokens must have. This must be a positive integer.
- ``-nmtl --no-min-token-length``: Tells the script to not filter tokens by length. Overrides the previous option.
- ``-sw --stopwords``: Tells the script to use the specified stopwords file. This file must be structured as one word per line.
- ``-nsw --no-stopwords``: Tells the script to not filter stopwords. Overrides the previous option.
- ``-nst --no-stemmer``: Tells the script to not stem the tokens.
- ``-memt --memory-threshold``: Tells the script how much of the total memory it is allowed to use. The value of the parameter must be between 0 and 1. This is a soft limit. it may go a little over the specified value. When absent defaults to 0.5
- ``-out --index-path``: Tells the script the path of the index file. If not specified it will default to `results/segmented_index`
- ``-if --indexing-format``: The indexing format to be used during the indexing process. If `none` is given as option it will skip the indexing phase. Defaults to `tf-idf` when absent.
- ``-d --debug``: Turn debug mode on. In this mode the script will overwrite the folder specified in ``-o --indexing-format`` if it exists. It will also not delete the temporary blocks used during the indexing phase.
- ``-k1``: K1 Parameter for BM25 Indexing.
- ``-b``: B Parameter for BM25 Indexing.
- ``-in --corpus-path``: Used to define the location of the corpus. When absent it will default to `data/amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz`.
- ``-qp --queries-path``: Tells the script where the queries to run are located at. When absent defaults to `data/queries.txt`.
- ``-rp --results-path``: Tells the script where to store the result of the queries. When absent defaults to `results/results.txt`.
- ``-qrp --query-relevance-path``: Tells the script where to find the query relevance file. When absent defaults to `data/queries.relevance.txt`.
- ``-ep --evaluation-path``: Tells the script where to store the evaluation results of the querying function. When absent defaults to `results/evaluation.txt`.
- ``-ql --query-limit``: Limits the number of results retrieved by the search function. When absent defaults to 100.