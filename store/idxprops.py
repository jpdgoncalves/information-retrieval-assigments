import json
import processor
from typing import Set
from definitions import IndexingFormat, IndexPropsDict, IndexProperties


def write_props(
        props_path: str,
        idx_format: IndexingFormat,
        index_size_on_disk: int,
        term_count: int,
        review_count: int,
        min_token_length: int,
        stopwords: Set[str],
        used_stemmer: bool
):
    with open(props_path, "w", encoding="utf-8") as props_file:
        props_dict: IndexPropsDict = {
            "idx_format": idx_format.value,
            "index_size_on_disk": index_size_on_disk,
            "term_count": term_count,
            "review_count": review_count,
            "min_token_length": min_token_length,
            "stopwords": list(stopwords),
            "stemmer": "english_stemmer" if used_stemmer else "no_stemmer"
        }
        json.dump(props_dict, props_file)


def read_props(
        props_path: str
) -> IndexProperties:
    with open(props_path, encoding="utf-8") as props_file:
        props_dict: IndexPropsDict = json.load(props_file)

        return IndexProperties(
            IndexingFormat(props_dict["idx_format"]),
            props_dict['index_size_on_disk'],
            props_dict['term_count'],
            props_dict['review_count'],
            props_dict['min_token_length'],
            set(props_dict['stopwords']),
            processor.english_stemmer if props_dict['stemmer'] == "english_stemmer" else processor.no_stemmer
        )
