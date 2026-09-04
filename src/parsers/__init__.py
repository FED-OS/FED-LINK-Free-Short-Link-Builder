"""Parsers for FED-LINk: turn links files into (slug, url) pairs.

Each parser accepts a path and returns ``list[tuple[str, str]]`` in file
order. Validation itself lives in ``validators`` so the parsers stay
simple and every frontend (CLI, GUI, dashboard) shares the same rules.

``load_links`` dispatches on file extension so callers never have to.
"""

import os

from src.parsers.json_parser import load_links_json
from src.parsers.yaml_parser import load_links_yaml
from src.parsers.csv_parser import load_links_csv

__all__ = [
    "load_links_json",
    "load_links_yaml",
    "load_links_csv",
    "load_links",
    "UnsupportedLinksFormatError",
]


class UnsupportedLinksFormatError(ValueError):
    """Raised when the links file has an unknown extension."""


def load_links(path: str) -> list[tuple[str, str]]:
    """Load links from ``.json``, ``.yaml``/``.yml`` or ``.csv``.

    The extension decides the parser; the result is always a list of
    ``(slug, url)`` pairs in the order they appear in the file.
    """
    extension = os.path.splitext(str(path))[1].lower()
    if extension == ".json":
        return load_links_json(path)
    if extension in (".yaml", ".yml"):
        return load_links_yaml(path)
    if extension == ".csv":
        return load_links_csv(path)
    raise UnsupportedLinksFormatError(
        f"unsupported links file extension '{extension}' for '{path}' — "
        "expected .json, .yaml/.yml or .csv"
    )
