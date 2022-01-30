from typing import List, Tuple, BinaryIO

from src.definitions import ReviewId, Offset, Length, DocId


def write_review_ids(review_ids_path: str, review_ids: List[ReviewId]):
    with open(review_ids_path, "a", encoding="utf-8") as review_ids_file:
        review_ids_file.writelines(f"{review_id}\n" for review_id in review_ids)


def review_id_reader(review_ids_path: str):
    locations = _load_review_ids_locations(review_ids_path)

    def read_review_id(review_file: BinaryIO, doc_id: DocId):
        # print(f"[reviews]: Getting review id for {doc_id}")
        offset, length = locations[doc_id]
        review_file.seek(offset)
        review_id = review_file.read(length).decode("utf-8").strip()
        # print(f"[reviews]: Found review id '{review_id}'")
        return review_id

    return read_review_id


def _load_review_ids_locations(review_ids_path: str) -> List[Tuple[Offset, Length]]:
    locations = []
    offset = 0
    with open(review_ids_path, encoding="utf-8", newline="\n") as review_id_file:
        for entry in review_id_file:
            length = len(entry.encode("utf-8"))
            locations.append((offset, length))
            offset += length

    return locations
