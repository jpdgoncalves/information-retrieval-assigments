from definitions import Path, Offset, PostingLen, PostingResults


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
            id_str, weight_str, positions_str = posting_str.split(":")

            doc_id = int(id_str)
            weight = float(weight_str)
            positions = [int(pos) for pos in positions_str.split(",")]

            yield doc_id + prev_doc_id, weight, positions

            prev_doc_id += doc_id
