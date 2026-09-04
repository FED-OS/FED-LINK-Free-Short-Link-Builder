"""CSV links parser.

Expected columns (header required): ``slug,url`` (the alias ``path`` is
accepted for urlzap compatibility). Order is flexible, extras are ignored,
and quoted URLs containing commas are handled by the csv module.

Example ``links.csv``::

    slug,url
    portfolio,https://example.github.io/portfolio
    game,https://example.github.io/game
"""

import csv

from src.utils.logger import get_logger
from src.parsers.json_parser import MalformedLinksFileError, _strip_prefix

_LOG = get_logger("parsers.csv")

_SLUG_HEADERS = ("slug", "path", "short", "code")
_URL_HEADERS = ("url", "target", "destination", "link")


def _find_columns(header: list[str]) -> tuple[int, int]:
    slug_index = url_index = -1
    for position, name in enumerate(header):
        clean = str(name).strip().lower()
        if clean in _SLUG_HEADERS and slug_index == -1:
            slug_index = position
        if clean in _URL_HEADERS and url_index == -1:
            url_index = position
    if slug_index == -1 or url_index == -1:
        raise MalformedLinksFileError(
            "CSV header must contain 'slug' and 'url' columns "
            f"(found: {header})"
        )
    return slug_index, url_index


def load_links_csv(path: str) -> list[tuple[str, str]]:
    """Read a CSV links file and return (slug, url) pairs in file order."""
    pairs: list[tuple[str, str]] = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if header is None:
                raise MalformedLinksFileError(f"'{path}' is empty")
            slug_index, url_index = _find_columns(header)

            for line, row in enumerate(reader, start=2):
                if not row or all(not cell.strip() for cell in row):
                    continue  # skip blank lines
                if len(row) <= max(slug_index, url_index):
                    raise MalformedLinksFileError(
                        f"'{path}' line {line}: expected at least "
                        f"{max(slug_index, url_index) + 1} columns, got {len(row)}"
                    )
                slug = _strip_prefix(row[slug_index])
                url = row[url_index].strip()
                if not slug or not url:
                    raise MalformedLinksFileError(
                        f"'{path}' line {line}: slug and url cannot be empty"
                    )
                pairs.append((slug, url))
    except csv.Error as exc:
        raise MalformedLinksFileError(f"'{path}' is not valid CSV: {exc}") from exc
    except OSError as exc:
        raise MalformedLinksFileError(f"cannot read '{path}': {exc}") from exc

    _LOG.debug("parsed %d link(s) from %s", len(pairs), path)
    return pairs
