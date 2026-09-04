"""JSON links parser.

Accepted shapes (in priority order):

1. Mapping of ``slug -> url`` (recommended, simplest)::

       {"portfolio": "https://example.github.io/portfolio"}

2. Sequence of mappings with ``path``/``url`` keys (urlzap-compatible)::

       [{"path": "/portfolio", "url": "https://example.github.io"}]

A sequence of 2-element arrays (``[["portfolio", "https://..."], ...]``)
also works, which makes migrating from older config styles painless.
"""

import json
from collections.abc import Mapping

from src.utils.logger import get_logger

_LOG = get_logger("parsers.json")


class MalformedLinksFileError(ValueError):
    """Raised when the JSON structure is unusable."""


def _strip_prefix(path: str) -> str:
    return str(path).strip().lstrip("/")


def _pairs_from_mapping(data: Mapping) -> list[tuple[str, str]]:
    return [(str(slug), str(url)) for slug, url in data.items()]


def _pairs_from_list(data: list) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for index, entry in enumerate(data):
        if isinstance(entry, Mapping):
            if "path" not in entry or "url" not in entry:
                raise MalformedLinksFileError(
                    f"entry #{index + 1} needs 'path' and 'url' keys: {entry!r}"
                )
            pairs.append((_strip_prefix(entry["path"]), str(entry["url"])))
        elif isinstance(entry, (list, tuple)) and len(entry) == 2:
            pairs.append((_strip_prefix(entry[0]), str(entry[1])))
        else:
            raise MalformedLinksFileError(
                f"entry #{index + 1} must be an object or [slug, url] pair: {entry!r}"
            )
    return pairs


def parse_links_payload(data: object) -> list[tuple[str, str]]:
    """Convert an already-loaded JSON payload into (slug, url) pairs."""
    if isinstance(data, Mapping):
        # {"links": {"slug": "url"}} or urlzap-style {"links": [{"path":...}]}
        if "links" in data:
            inner = data["links"]
            if isinstance(inner, Mapping):
                return _pairs_from_mapping(inner)
            if isinstance(inner, list):
                return _pairs_from_list(inner)
            raise MalformedLinksFileError(
                "the 'links' value must be an object or an array"
            )
        return _pairs_from_mapping(data)
    if isinstance(data, list):
        return _pairs_from_list(data)
    raise MalformedLinksFileError(
        "JSON root must be an object or an array of links"
    )


def load_links_json(path: str) -> list[tuple[str, str]]:
    """Read a JSON links file and return (slug, url) pairs in file order."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise MalformedLinksFileError(
            f"'{path}' is not valid JSON: {exc}"
        ) from exc
    except OSError as exc:
        raise MalformedLinksFileError(f"cannot read '{path}': {exc}") from exc

    pairs = parse_links_payload(data)
    _LOG.debug("parsed %d link(s) from %s", len(pairs), path)
    return pairs
