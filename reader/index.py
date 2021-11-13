"""
The Index Reader Module. Contains a single class that loads the terms to memory and the document frequency of the term.
"""
from typing import Dict


class IndexSearcher:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self._index: Dict[str, int] = {}

        self._load_index()

    def _load_index(self):
        with open(self.index_path, encoding="utf-8") as index_file:
            for line in index_file:
                term, *postings = line.split(";")
                self._index[term] = len(postings)

    def search_query(self, query: str):
        return self._index[query] if query in self._index else 0