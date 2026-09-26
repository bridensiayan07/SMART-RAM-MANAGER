"""
utils.py
--------
Small helper functions used by app.py:
    - parsing raw sidebar text into clean Python data structures
    - validating that input makes sense (with clear error messages)
    - formatting numbers nicely for the UI
"""

from typing import List, Tuple


class InputError(Exception):
    """Raised whenever sidebar input cannot be parsed or is invalid."""
    pass


def parse_blocks(raw_text: str) -> List[int]:
    """
    Convert a comma separated string such as "100,500,200" into [100, 500, 200].

    Raises InputError with a friendly message if something is wrong.
    """
    if not raw_text or not raw_text.strip():
        raise InputError("Memory Blocks field is empty. Example: 100,500,200")

    blocks = []
    for chunk in raw_text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.isdigit():
            raise InputError(f"'{chunk}' is not a valid block size. Use whole numbers only.")
        value = int(chunk)
        if value <= 0:
            raise InputError("Block sizes must be greater than 0.")
        blocks.append(value)

    if not blocks:
        raise InputError("No valid memory blocks were found.")

    return blocks


def parse_processes(raw_text: str) -> List[Tuple[str, int]]:
    """
    Convert "Chrome:300, VSCode:200" into [("Chrome", 300), ("VSCode", 200)].

    Raises InputError with a friendly message if something is wrong.
    """
    if not raw_text or not raw_text.strip():
        raise InputError("Applications field is empty. Example: Chrome:300, VSCode:200")

    processes = []
    for chunk in raw_text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise InputError(f"'{chunk}' must be in the form Name:Size, e.g. Chrome:300")

        name, size_str = chunk.split(":", 1)
        name = name.strip()
        size_str = size_str.strip()

        if not name:
            raise InputError("A process name is missing before ':' in your input.")
        if not size_str.isdigit():
            raise InputError(f"'{size_str}' is not a valid size for process '{name}'.")

        size = int(size_str)
        if size <= 0:
            raise InputError(f"Process '{name}' must request more than 0 MB.")

        processes.append((name, size))

    if not processes:
        raise InputError("No valid applications were found.")

    return processes


def format_mb(value: float) -> str:
    """Format a number as a memory size string, e.g. 512 -> '512 MB'."""
    if float(value).is_integer():
        return f"{int(value)} MB"
    return f"{value:.1f} MB"


def format_pct(value: float) -> str:
    """Format a number as a percentage string with 1 decimal place."""
    return f"{value:.1f}%"
