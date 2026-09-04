"""Tests for the JSON, YAML and CSV parsers."""

import os

import pytest

from src.parsers import (
    UnsupportedLinksFormatError,
    load_links,
    load_links_csv,
    load_links_json,
    load_links_yaml,
)
from src.parsers.json_parser import MalformedLinksFileError


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


class TestJsonParser:
    def test_mapping_root(self, tmp_path):
        path = _write(tmp_path, "links.json",
                      '{"portfolio": "https://example.com"}')
        assert load_links_json(path) == [("portfolio", "https://example.com")]

    def test_links_mapping_wrapper(self, tmp_path):
        path = _write(tmp_path, "links.json",
                      '{"links": {"a": "https://a.io", "b": "https://b.io"}}')
        assert load_links_json(path) == [
            ("a", "https://a.io"), ("b", "https://b.io")
        ]

    def test_urlzap_list_layout(self, tmp_path):
        path = _write(tmp_path, "links.json",
                      '{"links": [{"path": "/a", "url": "https://a.io"}]}')
        assert load_links_json(path) == [("a", "https://a.io")]

    def test_pair_arrays(self, tmp_path):
        path = _write(tmp_path, "links.json",
                      '[["a", "https://a.io"], ["b", "https://b.io"]]')
        assert load_links_json(path) == [
            ("a", "https://a.io"), ("b", "https://b.io")
        ]

    def test_project_config_parses(self):
        pairs = load_links_json("configs/links.json")
        assert ("portfolio", "https://fedpromptly.github.io/portfolio") in pairs
        assert len(pairs) == 10

    def test_invalid_json_raises(self, tmp_path):
        path = _write(tmp_path, "links.json", "{not json")
        with pytest.raises(MalformedLinksFileError):
            load_links_json(path)

    def test_missing_file_raises(self):
        with pytest.raises(MalformedLinksFileError):
            load_links_json("no/such/file.json")


class TestYamlParser:
    def test_mapping_root(self, tmp_path):
        path = _write(tmp_path, "links.yaml", "a: https://a.io\nb: https://b.io\n")
        assert load_links_yaml(path) == [
            ("a", "https://a.io"), ("b", "https://b.io")
        ]

    def test_urlzap_list_layout(self, tmp_path):
        path = _write(tmp_path, "links.yaml",
                      "links:\n  - path: /a\n    url: https://a.io\n")
        assert load_links_yaml(path) == [("a", "https://a.io")]

    def test_project_config_parses(self):
        pairs = load_links_yaml("configs/links.yaml")
        assert len(pairs) == 10
        assert dict(pairs)["kofi"] == "https://ko-fi.com/fedpromptly"

    def test_empty_document_returns_empty_list(self, tmp_path):
        path = _write(tmp_path, "links.yaml", "")
        assert load_links_yaml(path) == []


class TestCsvParser:
    def test_basic_csv(self, tmp_path):
        path = _write(tmp_path, "links.csv",
                      "slug,url\na,https://a.io\nb,https://b.io\n")
        assert load_links_csv(path) == [
            ("a", "https://a.io"), ("b", "https://b.io")
        ]

    def test_quoted_urls_with_commas(self, tmp_path):
        path = _write(tmp_path, "links.csv",
                      'slug,url\na,"https://a.io/x,y"\n')
        assert load_links_csv(path) == [("a", "https://a.io/x,y")]

    def test_header_aliases(self, tmp_path):
        path = _write(tmp_path, "links.csv",
                      "path,destination\na,https://a.io\n")
        assert load_links_csv(path) == [("a", "https://a.io")]

    def test_skips_blank_lines(self, tmp_path):
        path = _write(tmp_path, "links.csv",
                      "slug,url\n\na,https://a.io\n\n")
        assert load_links_csv(path) == [("a", "https://a.io")]

    def test_missing_url_column_raises(self, tmp_path):
        path = _write(tmp_path, "links.csv", "slug\na\n")
        with pytest.raises(MalformedLinksFileError):
            load_links_csv(path)

    def test_short_row_raises(self, tmp_path):
        path = _write(tmp_path, "links.csv", "slug,url\na\n")
        with pytest.raises(MalformedLinksFileError):
            load_links_csv(path)


class TestLoadLinksDispatcher:
    def test_dispatches_by_extension(self, tmp_path):
        json_path = _write(tmp_path, "links.json", '{"a": "https://a.io"}')
        assert load_links(json_path) == [("a", "https://a.io")]

    def test_unknown_extension_raises(self, tmp_path):
        path = _write(tmp_path, "links.txt", "a https://a.io")
        with pytest.raises(UnsupportedLinksFormatError):
            load_links(path)
