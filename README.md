# Information Retrieval Assigments

## Prepare the environment
- Create a virtual environment (Python 3.9)
- Active the virtual environment
- Install the requirements in `requirements.txt`

## Run the Code
- Activate the virtual environment if it isn't already
- Run ```python main.py [options] <corpus_file_path>```

With this configuration the script will create an index file
called `index.txt`. The tokens will have a length equal or larger
than 3 characters, stopwords will be filtered and words will be stemmed

Regardless of configuration after indexing is done, a simple reader
will be ran that takes a single word as input and prints out, the number
of documents with said word.

## Command Options

- ``-mtl --min-token-length <length>``: Defines the minimum length the tokens must have. This must be a positive integer.
- ``-nmtl --no-min-token-length``: Tells the script to not filter tokens by length. Overrides the previous option.
- ``-sw --stopwords``: Tells the script to use the specified stopwords file. This file must be structured as one word per line.
- ``-nsw --no-stopwords``: Tells the script to not filter stopwords. Overrides the previous option.
- ``-nst --no-stemmer``: Tells the script to not stem the tokens.
- ``-o --index-path``: Tells the script the path of the index file. If not specified it will default to `index.txt`