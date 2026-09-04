"""Writes the final folder structure for InfinityFree's ``htdocs``.

Layout produced inside the output directory::

    output/
    ├── .htaccess          Apache 301 rules + 404 fallback
    ├── 404.html           fallback page for unknown links
    ├── links.json         machine-readable manifest
    └── <slug>/index.html  one redirect page per short link

``.htaccess`` is written from ``configs/.htaccess.template`` when present
(the generator also embeds a fallback template so a missing file can never
break a build). Only the generator-owned entries are cleaned between runs,
so manual files survive.
"""

import os

from src.generator.html_builder import HtmlBuilder
from src.utils.file_cleaner import clean_directory, ensure_directory
from src.utils.logger import get_logger
from src.validators import validate_links

_LOG = get_logger("generator.folder_creator")

_FALLBACK_HTACCESS = """# FED-LINk — generated .htaccess (fallback template)
Options -Indexes

RewriteEngine On

{{redirects}}

# Unknown short links fall back to the main site
ErrorDocument 404 /404.html
"""

_REDIRECT_LINE = "Redirect 301 /{slug} {url}"


class FolderCreator:
    """Turns a validated link mapping into the deployable folder tree."""

    def __init__(self, output_dir: str = "output",
                 template_path: str | None = None,
                 htaccess_template: str | None = None,
                 site_domain: str = "link.fedpromptly.com",
                 home_url: str = "https://fedpromptly.com") -> None:
        self.output_dir = output_dir
        self.builder = HtmlBuilder(template_path, site_domain=site_domain)
        self.htaccess_template = self._load_htaccess_template(htaccess_template)
        self.home_url = home_url

    # ------------------------------------------------------------------ #
    # setup
    # ------------------------------------------------------------------ #
    def _load_htaccess_template(self, path: str | None) -> str:
        if not path:
            return _FALLBACK_HTACCESS
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read()
        except OSError as exc:
            _LOG.warning(
                "could not read .htaccess template '%s' (%s); using built-in default",
                path, exc,
            )
            return _FALLBACK_HTACCESS

    # ------------------------------------------------------------------ #
    # planning (v1.1, ROADMAP: ``--dry-run``)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _read_if_exists(path: str) -> str | None:
        """Return file contents, or ``None`` when the file is absent."""
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read()
        except OSError:
            return None

    def plan(self, links: object) -> dict[str, object]:
        """Preview what ``generate()`` would write, without touching disk.

        Returns a JSON-ready dict describing the next build::

            {
              "actions":     {slug: "create" | "update" | "keep", ...},
              "stale":       [slugs whose folders exist but are not in the links file],
              "write_404":   bool,   # 404.html missing or different
              "write_htaccess": bool,
              "write_manifest": bool,
              "clean":       bool    # anything to remove (stale folders)
            }

        A page counts as ``keep`` only when it is byte-identical to what
        ``generate()`` would render, so template tweaks surface as updates.
        """
        mapping = validate_links(links)

        actions: dict[str, str] = {}
        for slug, url in mapping.items():
            page_path = os.path.join(self.output_dir, slug, "index.html")
            existing = self._read_if_exists(page_path)
            if existing is None:
                actions[slug] = "create"
            elif existing == self.builder.build_redirect_page(slug, url):
                actions[slug] = "keep"
            else:
                actions[slug] = "update"

        present: set[str] = set()
        if os.path.isdir(self.output_dir):
            present = {
                entry for entry in os.listdir(self.output_dir)
                if not entry.startswith(".")
            }
        owned = {".htaccess", "404.html", "links.json"}
        stale = sorted(present - owned - set(mapping))

        expected_404 = self.builder.build_404_page(home_url=self.home_url)
        expected_manifest = self.builder.build_manifest(mapping)
        expected_htaccess = self._render_htaccess(mapping)

        def needs_write(name: str, expected: str) -> bool:
            path = os.path.join(self.output_dir, name)
            return self._read_if_exists(path) != expected

        plan = {
            "actions": actions,
            "stale": stale,
            "write_404": needs_write("404.html", expected_404),
            "write_htaccess": needs_write(".htaccess", expected_htaccess),
            "write_manifest": needs_write("links.json", expected_manifest),
        }
        plan["clean"] = bool(stale)
        plan["changes"] = (
            any(action != "keep" for action in actions.values())
            or plan["clean"]
            or plan["write_404"] or plan["write_htaccess"] or plan["write_manifest"]
        )
        return plan

    # ------------------------------------------------------------------ #
    # generation
    # ------------------------------------------------------------------ #
    def generate(self, links: object, clean: bool = True) -> dict[str, str]:
        """Generate the full tree; return ``{relative_path: destination}``.

        ``links`` may be any iterable of (slug, url) pairs; it is validated
        here so a direct API call gets the same guarantees as the CLI.
        With ``clean=True`` (default) the output directory is emptied of
        generator-owned files first, so deleted links cannot linger.
        """
        mapping = validate_links(links)
        if clean:
            removed = clean_directory(self.output_dir)
            if removed:
                _LOG.info("cleaned %d stale entr%s from %s",
                          removed, "y" if removed == 1 else "ies", self.output_dir)
        ensure_directory(self.output_dir)

        written: dict[str, str] = {}

        for slug, url in mapping.items():
            page = self.builder.build_redirect_page(slug, url)
            slug_dir = os.path.join(self.output_dir, slug)
            ensure_directory(slug_dir)
            page_path = os.path.join(slug_dir, "index.html")
            self._write(page_path, page)
            written[os.path.join(slug, "index.html")] = url

        self._write(os.path.join(self.output_dir, "404.html"),
                    self.builder.build_404_page(home_url=self.home_url))
        self._write(os.path.join(self.output_dir, "links.json"),
                    self.builder.build_manifest(mapping))
        self._write(os.path.join(self.output_dir, ".htaccess"),
                    self._render_htaccess(mapping))

        _LOG.info("generated %d short link(s) into %s", len(mapping), self.output_dir)
        return written

    def _render_htaccess(self, mapping: dict[str, str]) -> str:
        redirects = "\n".join(
            _REDIRECT_LINE.format(slug=slug, url=url)
            for slug, url in mapping.items()
        )
        return self.builder.render(self.htaccess_template, {
            "redirects": redirects,
            "site_domain": self.builder.site_domain,
            "home_url": self.home_url,
        })

    @staticmethod
    def _write(path: str, content: str) -> None:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        _LOG.debug("wrote %s", path)
