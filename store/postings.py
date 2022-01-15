from typing import List
from definitions import Path, Offset, PostingLen, PostingResults, Postings


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


def deserialize_positions(data: str):
    return [int(pos) for pos in data.split(",")]


def deserialize_posting(data: str):
    doc_id, weight, positions = data.split(":")
    return int(doc_id), float(weight), deserialize_positions(positions)


def deserialize_postings(data):
    return [deserialize_posting(posting) for posting in data.split(";")]


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
