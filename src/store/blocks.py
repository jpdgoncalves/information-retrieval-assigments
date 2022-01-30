from typing import List, Generator, TextIO, Optional
from definitions import Vocabulary, TermPostingsEntry, Block
from store.postings import serialize_postings, deserialize_postings

import heapq


def write_block(block_path: str, vocabulary: Vocabulary):

    with open(block_path, "w", newline="\n") as block_file:
        print(f"[BlockWriter]: Writing {block_path}")

        sorted_terms = sorted(vocabulary.keys())

        for term in sorted_terms:
            block_file.write(f"{term};{serialize_postings(vocabulary[term])}\n")

        print(f"[BlockWriter]: Finished writing {block_path}")


def _block(block_path: Optional[str] = None, *, f: Optional[TextIO] = None) -> Optional[Block]:
    block_file: TextIO = f if block_path is None else open(block_path)
    block_line = block_file.readline()

    if len(block_line) == 0:
        block_file.close()
        return None

    term, posting_data = block_line.split(";", 1)
    postings = deserialize_postings(posting_data)
    return term, postings[0][0], postings, block_file


def _next_postings(blocks: List[Block]) -> TermPostingsEntry:
    top_block = heapq.heappop(blocks)
    term, _, postings, block_file = top_block

    new_block = _block(f=block_file)

    if new_block is not None:
        heapq.heappush(blocks, new_block)

    return term, postings


def blocks_iterator(block_paths: List[str]) -> Generator[TermPostingsEntry, None, None]:
    """
    Iterates through a list of block files. This iterator takes care of
    reading the postings by term and docId order and of aggregating postings
    of the same terms into a single postings, yielding that as the result of
    each iteration.
    :param block_paths:
    :return:
    """
    blocks = [_block(block_path) for block_path in block_paths]
    heapq.heapify(blocks)

    accum_postings = _next_postings(blocks)

    while len(blocks) != 0:
        term, postings = _next_postings(blocks)

        if accum_postings[0] != term:
            yield accum_postings
            accum_postings = (term, postings)
        else:
            accum_postings[1].extend(postings)

    yield accum_postings
