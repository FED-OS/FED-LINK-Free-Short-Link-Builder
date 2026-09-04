"""End-to-end tests for the generator: folders, pages, .htaccess, ZIP."""

import os
import zipfile

import pytest

from src.generator.folder_creator import FolderCreator
from src.generator.html_builder import HtmlBuilder
from src.generator.zip_packager import ZipPackager
from src.validators import LinkValidationError

EXPECTED_SAMPLE_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, follow">
<title>sample</title>
<link rel="canonical" href="https://example.github.io/sample">
<meta http-equiv="refresh" content="0; url=https://example.github.io/sample">
</head>
<body>
<p>Redirecting to <a href="https://example.github.io/sample">https://example.github.io/sample</a>&hellip;</p>
<script>window.location.replace("https://example.github.io/sample");</script>
</body>
</html>
"""

LINKS = [
    ("sample", "https://example.github.io/sample"),
    ("blog", "https://example.github.io/blog"),
]


@pytest.fixture()
def creator(tmp_path):
    return FolderCreator(
        output_dir=str(tmp_path / "output"),
        htaccess_template=None,  # use the built-in fallback template
        site_domain="link.fedpromptly.com",
        home_url="https://fedpromptly.com",
    )


class TestFolderCreator:
    def test_creates_one_folder_per_link(self, creator, tmp_path):
        creator.generate(LINKS)
        output = tmp_path / "output"
        assert (output / "sample" / "index.html").is_file()
        assert (output / "blog" / "index.html").is_file()

    def test_redirect_page_matches_expected_fixture(self, creator):
        page = creator.builder.build_redirect_page(
            "sample", "https://example.github.io/sample")
        assert page == EXPECTED_SAMPLE_PAGE

    def test_htaccess_contains_redirect_rules(self, creator, tmp_path):
        creator.generate(LINKS)
        htaccess = (tmp_path / "output" / ".htaccess").read_text(encoding="utf-8")
        assert "Redirect 301 /sample https://example.github.io/sample" in htaccess
        assert "Redirect 301 /blog https://example.github.io/blog" in htaccess
        assert "ErrorDocument 404 /404.html" in htaccess

    def test_htaccess_template_is_used_when_available(
            self, tmp_path, monkeypatch):
        template = tmp_path / "custom.htaccess"
        template.write_text(
            "# custom\n{{redirects}}\nErrorDocument 404 /404.html\n",
            encoding="utf-8")
        creator = FolderCreator(
            output_dir=str(tmp_path / "out"),
            htaccess_template=str(template),
        )
        creator.generate(LINKS)
        content = (tmp_path / "out" / ".htaccess").read_text(encoding="utf-8")
        assert content.startswith("# custom")
        assert "Redirect 301 /sample" in content

    def test_manifest_lists_every_link(self, creator, tmp_path):
        creator.generate(LINKS)
        manifest = (tmp_path / "output" / "links.json").read_text(encoding="utf-8")
        assert '"sample"' in manifest
        assert '"count": 2' in manifest

    def test_404_page_written(self, creator, tmp_path):
        creator.generate(LINKS)
        page404 = (tmp_path / "output" / "404.html").read_text(encoding="utf-8")
        assert "fedpromptly.com" in page404

    def test_clean_removes_stale_folders(self, creator, tmp_path):
        creator.generate(LINKS)
        stale = tmp_path / "output" / "deleted-link" / "index.html"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("stale", encoding="utf-8")
        creator.generate([("sample", "https://example.github.io/sample")])
        assert not stale.exists()

    def test_keep_file_survives_clean(self, creator, tmp_path):
        keep = tmp_path / "output" / ".keep"
        keep.parent.mkdir(parents=True, exist_ok=True)
        keep.write_text("", encoding="utf-8")
        creator.generate(LINKS)
        assert keep.exists()

    def test_generate_validates_input(self, creator):
        with pytest.raises(LinkValidationError):
            creator.generate([("bad slug", "https://example.com")])

    def test_project_config_generates_all_ten_links(self, tmp_path):
        from src.parsers import load_links_json
        creator = FolderCreator(output_dir=str(tmp_path / "out"))
        creator.generate(load_links_json("configs/links.json"))
        out = tmp_path / "out"
        for slug in ("portfolio", "game", "docs", "blog", "resume",
                     "shop", "app", "tools", "contact", "kofi"):
            assert (out / slug / "index.html").is_file(), slug


class TestHtmlBuilder:
    def test_renders_placeholders(self):
        builder = HtmlBuilder()
        page = builder.build_redirect_page("x", "https://x.io")
        assert '<meta http-equiv="refresh" content="0; url=https://x.io">' in page
        assert 'window.location.replace("https://x.io")' in page

    def test_js_string_is_escaped(self):
        builder = HtmlBuilder()
        page = builder.build_redirect_page("x", 'https://x.io/{"weird"}')
        assert 'window.location.replace("https://x.io/{\\"weird\\"}")' in page

    def test_unknown_placeholders_are_left_alone(self):
        builder = HtmlBuilder()
        rendered = builder.render("keep {{ nope }} and {{known}}",
                                  {"known": "value"})
        assert "{{ nope }}" in rendered
        assert "value" in rendered

    def test_404_page_mentions_requested_link(self):
        builder = HtmlBuilder()
        page = builder.build_404_page(requested="/ghost")
        assert "/ghost" in page


class TestZipPackager:
    def test_zip_contains_the_bundle(self, creator, tmp_path):
        creator.generate(LINKS)
        packager = ZipPackager(
            source_dir=str(tmp_path / "output"),
            zip_path=str(tmp_path / "links.zip"),
        )
        zip_path, count = packager.package()
        names = zipfile.ZipFile(zip_path).namelist()
        assert count == len(names)
        assert "sample/index.html" in names
        assert ".htaccess" in names
        assert ".keep" not in names  # excluded on purpose

    def test_missing_source_raises(self, tmp_path):
        packager = ZipPackager(
            source_dir=str(tmp_path / "nope"),
            zip_path=str(tmp_path / "links.zip"),
        )
        with pytest.raises(FileNotFoundError):
            packager.package()


class TestPlan:
    """``plan()`` / ``--dry-run`` (v1.1): preview without writing."""

    def test_empty_output_plans_create_for_every_link(self, creator):
        plan = creator.plan(LINKS)
        assert plan["actions"] == {"sample": "create", "blog": "create"}
        assert plan["stale"] == []
        assert plan["changes"] is True

    def test_fresh_build_plans_keep_for_every_link(self, creator):
        creator.generate(LINKS)
        plan = creator.plan(LINKS)
        assert plan["actions"] == {"sample": "keep", "blog": "keep"}
        assert plan["stale"] == []
        # support files were just written from the same inputs
        assert plan["write_404"] is False
        assert plan["write_htaccess"] is False
        assert plan["write_manifest"] is False
        assert plan["clean"] is False
        assert plan["changes"] is False

    def test_changed_url_plans_update(self, creator):
        creator.generate(LINKS)
        changed = [("sample", "https://example.github.io/renamed"),
                   ("blog", "https://example.github.io/blog")]
        plan = creator.plan(changed)
        assert plan["actions"]["sample"] == "update"
        assert plan["actions"]["blog"] == "keep"
        assert plan["changes"] is True

    def test_removed_link_is_stale_and_needs_clean(self, creator):
        creator.generate(LINKS)
        plan = creator.plan([("sample", "https://example.github.io/sample")])
        assert plan["stale"] == ["blog"]
        assert plan["clean"] is True
        assert plan["changes"] is True

    def test_new_link_alongside_existing(self, creator):
        creator.generate(LINKS)
        grown = LINKS + [("new", "https://example.github.io/new")]
        plan = creator.plan(grown)
        assert plan["actions"]["new"] == "create"
        assert plan["actions"]["sample"] == "keep"

    def test_plan_writes_nothing(self, creator, tmp_path):
        creator.plan(LINKS)
        output = tmp_path / "output"
        assert not output.exists()

    def test_plan_is_json_ready(self, creator):
        import json
        plan = creator.plan(LINKS)
        round_tripped = json.loads(json.dumps(plan))
        assert round_tripped == plan

    def test_plan_validates_links_first(self, creator):
        with pytest.raises(LinkValidationError):
            creator.plan([("bad slug", "https://example.com/")])
