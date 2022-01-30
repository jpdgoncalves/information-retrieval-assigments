import math
from typing import List
from src.definitions import Path, Offset, PostingLen, PostingResults, Postings


def serialize_positions(positions: List[int]):
    return ",".join([str(pos) for pos in positions])


def serialize_posting(doc_id: int, weight: float, positions: List[int]):
    return f"{doc_id}:{weight}:{serialize_positions(positions)}"


def serialize_postings(postings: Postings):
    return ";".join(serialize_posting(doc_id, weight, positions) for doc_id, weight, positions in postings)


def serialize_as_postings(doc_ids: List[int], weights: List[float], l_pos: List[List[int]]):
    return ";".join(
        serialize_posting(doc_id, weight, positions) for doc_id, weight, positions in zip(doc_ids, weights, l_pos)
    )


def serial_as_posts_with_diffs(
    doc_ids: List[int], weights: List[float], l_pos: List[List[int]]
):
    """
    Serializes the postings with doc ids encoded as differences rather than the full doc id.
    """
    doc_diffs = [doc_ids[0]] + [doc_ids[i+1] - doc_ids[i] for i in range(0, len(doc_ids)-1)]
    return serialize_as_postings(doc_diffs, weights, l_pos)


def deserialize_positions(data: str):
    return [int(pos) for pos in data.split(",")]


def deserialize_posting(data: str):
    doc_id, weight, positions = data.split(":")
    return int(doc_id), float(weight), deserialize_positions(positions)


def deserialize_postings(data: str) -> Postings:
    return [deserialize_posting(posting) for posting in data.split(";")]


def write_tf_idf_postings(
        postings_path: str,
        l_postings: List[Postings],
        *,
        review_count: int
):
    cur_offset = 0
    results = []

    with open(postings_path, "wb", buffering=1024 * 1024) as postings_file:
        for postings in l_postings:
            idf = math.log10(review_count / len(postings))
            doc_ids, weights, l_positions = tuple(zip(*postings))

            byte_len = postings_file.write(
                f"{serial_as_posts_with_diffs(doc_ids, weights, l_positions)}\n".encode("utf-8")
            )

            results.append((idf, cur_offset, byte_len))
            cur_offset += byte_len

    return tuple(zip(*results))


def write_bm25_postings(
        postings_path: str,
        l_postings: List[Postings],
        *,
        review_count: int,
        avg_dl: float,
        document_lengths: List[int],
        b: float,
        k1: float
):
    cur_offset = 0
    results = []

    with open(postings_path, "wb", buffering=1024 * 1024) as postings_file:
        for postings in l_postings:
            idf = math.log10(review_count / len(postings))
            doc_ids, tfs, l_positions = tuple(zip(*postings))
            doc_lens = [document_lengths[doc_id] for doc_id in doc_ids]
            weights = [_bm25_weight(avg_dl, doc_len, b, k1, idf, tf) for doc_len, tf in zip(doc_lens, tfs)]

            byte_len = postings_file.write(
                f"{serial_as_posts_with_diffs(doc_ids, weights, l_positions)}\n".encode("utf-8")
            )

            results.append((cur_offset, byte_len))
            cur_offset += byte_len

    return tuple(zip(*results))


def _bm25_weight(avg_dl: float, doc_len: int, b: float, k1: float, idf: float, tf: int):
    b_normalizer = 1 - b + b * (doc_len / avg_dl)
    return idf * ((k1 + 1) * tf) / (k1 * b_normalizer + tf)


def read_postings(
        segment_path: Path,
        offset: Offset,
        post_len: PostingLen
) -> PostingResults:
    prev_doc_id = 0

    with open(f"{segment_path}/postings.txt", "rb") as posts_file:
        posts_file.seek(offset)
        postings_data = posts_file.read(post_len).decode("utf-8").strip().split(";")

        for posting_str in postings_data:
            doc_id, weight, positions = deserialize_posting(posting_str)

            yield doc_id + prev_doc_id, weight, positions

            prev_doc_id += doc_id
