"""
memory_algorithms.py
---------------------
Implements three classic Operating System memory allocation strategies:

    1. First Fit  - place the process in the FIRST block big enough for it
    2. Best Fit   - place the process in the SMALLEST block that still fits
    3. Worst Fit  - place the process in the LARGEST available block

MODEL USED
----------
Each physical memory block can hold AT MOST one process (this is the
classic "fixed / static partitioning" model that is normally used to
teach First / Best / Worst Fit). Once a block is handed to a process,
any leftover space inside that block becomes "internal fragmentation"
-- wasted space that cannot be reused by any other process.

RETURN VALUES
-------------
Every function below returns a tuple: (allocation, block_status)

    allocation   -> a list the same length as `processes`.
                    allocation[i] tells us which block processes[i] got.
                        - an integer  -> index of the block it was placed in
                        - None        -> could not be allocated (no block big enough)

    block_status -> a list the same length as `blocks`.
                    block_status[j] tells us the state of block j AFTER
                    allocation finished.
                        - -1                -> block is now USED (given to a process)
                        - blocks[j] (int)   -> block is still completely FREE
"""

from typing import List, Tuple, Optional, Callable


def _allocate(
    blocks: List[int],
    processes: List[Tuple[str, int]],
    pick_block_index: Callable[[List[Tuple[int, int]]], int],
) -> Tuple[List[Optional[int]], List[int]]:
    """
    Shared allocation engine used by all three strategies below.

    `pick_block_index` decides WHICH block to choose out of all the
    blocks that are big enough for the current process. Each strategy
    (first/best/worst fit) just supplies a different picking rule.
    """
    block_status = blocks.copy()          # working copy we can mutate
    allocation: List[Optional[int]] = [None] * len(processes)

    for i, (_name, size) in enumerate(processes):
        # Find every free block that is large enough for this process
        candidates = [
            (j, block_status[j])
            for j in range(len(block_status))
            if block_status[j] != -1 and block_status[j] >= size
        ]

        if not candidates:
            allocation[i] = None          # no block was big enough
            continue

        chosen_index = pick_block_index(candidates)
        allocation[i] = chosen_index
        block_status[chosen_index] = -1   # this block is now used up

    return allocation, block_status


def first_fit(blocks: List[int], processes: List[Tuple[str, int]]):
    """Give each process the FIRST free block that is big enough."""
    return _allocate(blocks, processes, lambda cands: cands[0][0])


def best_fit(blocks: List[int], processes: List[Tuple[str, int]]):
    """Give each process the SMALLEST free block that still fits it."""
    return _allocate(
        blocks,
        processes,
        lambda cands: min(cands, key=lambda c: c[1])[0],
    )


def worst_fit(blocks: List[int], processes: List[Tuple[str, int]]):
    """Give each process the LARGEST free block available."""
    return _allocate(
        blocks,
        processes,
        lambda cands: max(cands, key=lambda c: c[1])[0],
    )


# Handy lookup used by app.py when it needs to run "all algorithms"
ALGORITHMS = {
    "First Fit": first_fit,
    "Best Fit": best_fit,
    "Worst Fit": worst_fit,
}
