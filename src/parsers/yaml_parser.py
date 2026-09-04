"""YAML links parser.

Accepted shapes (same as the JSON parser):

1. Mapping of ``slug -> url``::

       portfolio: https://example.github.io/portfolio
       game: https://example.github.io/game

2. urlzap-compatible list::

       links:
         - path: /portfolio
           url: https://example.github.io/portfolio

YAML is optional at runtime: importing this module only fails when YAML
input is actually requested, so the CLI/JSON path stays dependency-free.
"""

from collections.abc import Mapping

from src.utils.logger import get_logger
from src.parsers.json_parser import (
    MalformedLinksFileError,
    _pairs_from_list,
    _pairs_from_mapping,
    _strip_prefix,
)

_LOG = get_logger("parsers.yaml")


def _import_yaml():
    try:
        import yaml  # noqa: PLC0415 - deferred on purpose
    except ImportError as exc:  # pragma: no cover - depends on install
        raise MalformedLinksFileError(
            "PyYAML is required for YAML links files "
            "(pip install pyyaml)"
        ) from exc
    return yaml


def parse_links_document(data: object) -> list[tuple[str, str]]:
    """Convert an already-loaded YAML document into (slug, url) pairs."""
    if isinstance(data, Mapping):
        if "links" in data:
            inner = data["links"]
            if isinstance(inner, Mapping):
                return _pairs_from_mapping(inner)
            if isinstance(inner, list):
                return _pairs_from_list(inner)
            raise MalformedLinksFileError(
                "the 'links' value must be a mapping or a list"
            )
        return _pairs_from_mapping(data)
    if isinstance(data, list):
        return _pairs_from_list(data)
    raise MalformedLinksFileError(
        "YAML root must be a mapping or a list of links"
    )


def load_links_yaml(path: str) -> list[tuple[str, str]]:
    """Read a YAML links file and return (slug, url) pairs in file order."""
    yaml = _import_yaml()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        raise MalformedLinksFileError(f"cannot read '{path}': {exc}") from exc

    if data is None:  # empty file
        return []

    pairs = parse_links_document(data)
    _LOG.debug("parsed %d link(s) from %s", len(pairs), path)
    return pairs
