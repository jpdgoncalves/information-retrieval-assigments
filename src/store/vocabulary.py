from typing import List, Optional, Tuple

from src.definitions import Segment, Term, BM25Metadata, IdfMetadata, Path


def serialize_tf_idf_metadata(term: str, idf: float, offset: int, byte_len: int):
    return f"{term}:{idf}:{offset}:{byte_len}\n"


def deserialize_tf_idf_metadata(data: str) -> IdfMetadata:
    term, idf, offset, byte_len = data.split(":")
    return term, float(idf), int(offset), int(byte_len)


def serialize_bm25_metadata(term: str, offset: int, byte_len: int):
    return f"{term}:{offset}:{byte_len}\n"


def deserialize_bm25_metadata(data: str) -> BM25Metadata:
    term, offset, byte_len = data.split(":")
    return term, int(offset), int(byte_len)


def write_tf_idf_vocabulary(
        vocab_path: str, terms: list[str], idfs: list[float],
        offsets: list[int], lengths: list[int]
):
    with open(vocab_path, "w", encoding="utf-8", newline="\n") as vocab_file:
        for term, idf, offset, length in zip(terms, idfs, offsets, lengths):
            vocab_file.write(serialize_tf_idf_metadata(term, idf, offset, length))


def write_bm25_vocabulary(
        vocab_path: str, terms: list[str],
        offsets: list[int], lengths: list[int]
):
    with open(vocab_path, "w", encoding="utf-8", newline="\n") as vocab_file:
        for term, offset, length in zip(terms, offsets, lengths):
            vocab_file.write(serialize_bm25_metadata(term, offset, length))


def bm25_metadata_reader(segments: List[Segment]):
    def read(term: Term) -> Optional[BM25Metadata]:
        # print(f"[vocabulary]: Searching for term '{term}'")
        metadata = _get_metadata(segments, term)
        # print(f"[vocabulary] Found metadata {metadata}")

        if metadata is None:
            return None

        segment_path, term_metadata = metadata

        offset_str, post_len_str = term_metadata.split(":")
        return segment_path, int(offset_str), int(post_len_str)

    return read


def tf_idf_metadata_reader(segments: List[Segment]):
    def read(term: Term) -> Optional[IdfMetadata]:
        # print(f"[vocabulary]: Searching for term '{term}'")
        metadata = _get_metadata(segments, term)
        # print(f"[vocabulary] Found metadata {metadata}")

        if metadata is None:
            return None

        segment_path, term_metadata = metadata

        idf_str, offset_str, post_len_str = term_metadata.split(":")

        return segment_path, float(idf_str), int(offset_str), int(post_len_str)

    return read


def _get_metadata(segments: List[Segment], term: Term) -> Optional[Tuple[Path, str]]:
    segment_path = _find_segment(segments, term)
    # print(f"[vocabulary]: Found segment '{segment_path}'")

    if segment_path is None:
        return None

    with open(f"{segment_path}/vocabulary.txt", encoding="utf-8") as vocab_file:
        vocabulary_entries = [vocab_entry.strip().split(":", 1) for vocab_entry in vocab_file]

    metadata = _find_metadata(vocabulary_entries, term)

    if metadata is None:
        return None

    return segment_path, metadata


def _find_segment(segments: List[Segment], term: Term) -> Optional[Path]:
    """
    Taking an ordered list of segments and a term to search
    this function returns the segment_path of the segment this term belongs to
    if it is found. Otherwise it returns None.
    Algorithm from https://en.wikipedia.org/wiki/Binary_search_algorithm#Procedure
    :param segments:
    :param term:
    :return:
    """
    left = 0
    right = len(segments) - 1

    while left <= right:
        mid = (left + right) // 2

        if segments[mid][1] < term:
            left = mid + 1
        elif segments[mid][0] > term:
            right = mid - 1
        else:
            return segments[mid][2]

    return None


def _find_metadata(vocabulary_entries: List[Tuple[Term, str]], term: Term) -> Optional[str]:
    """
    Taking an ordered list of terms and a term to search
    this function returns the metadata of the term in the vocabulary
    if it is found. Otherwise it returns None.

    Algorithm from https://en.wikipedia.org/wiki/Binary_search_algorithm#Procedure
    :param vocabulary_entries:
    :param term:
    :return:
    """
    left = 0
    right = len(vocabulary_entries) - 1

    while left <= right:
        mid = (left + right) // 2

        if vocabulary_entries[mid][0] < term:
            left = mid + 1
        elif vocabulary_entries[mid][0] > term:
            right = mid - 1
        else:
            return vocabulary_entries[mid][1]

    return None
