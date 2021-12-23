from definitions import Path, Offset, PostingLen, PostingResults


def read_postings(
        segment_path: Path,
        offset: Offset,
        post_len: PostingLen
) -> PostingResults:
    postings = []
    prev_doc_id = 0

    with open(f"{segment_path}/postings.txt", "rb") as posts_file:
        posts_file.seek(offset)
        postings_data = posts_file.read(post_len).decode("utf-8").strip()

        for posting_str in postings_data.split(";"):
            id_str, weight_str, positions_str = posting_str.split(":")
            doc_id, weight, positions = int(id_str), float(weight_str), [int(pos) for pos in positions_str.split(",")]

            postings.append(
                (doc_id + prev_doc_id, weight, positions)
            )

            prev_doc_id += doc_id

    return postings
