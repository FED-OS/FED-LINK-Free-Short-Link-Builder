"""Renders the redirect pages and support files for FED-LINk.

Two formats are produced per link:

* ``index.html`` — meta-refresh redirect with a JS fallback and a visible
  link, so it works on GitHub Pages, static hosts and InfinityFree alike
* ``links.json`` — machine-readable manifest so tools (and the dashboard)
  can introspect the live build

The page template is a Jinja-style ``{{ placeholder }}`` file loaded from
``templates/``; placeholders are filled with a tiny, dependency-free
string formatter so the generator works without Jinja installed.
"""

import json
import os
import re
from datetime import datetime, timezone

from src.utils.logger import get_logger

_LOG = get_logger("generator.html_builder")

_PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")

_DEFAULT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, follow">
<title>{{slug}}</title>
<link rel="canonical" href="{{url}}">
<meta http-equiv="refresh" content="0; url={{url}}">
</head>
<body>
<p>Redirecting to <a href="{{url}}">{{url}}</a>&hellip;</p>
<script>window.location.replace({{url_js}});</script>
</body>
</html>
"""

_NOT_FOUND_BODY = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Link not found — FED-LINk</title>
<style>
:root { color-scheme: light dark; }
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  display: grid; place-items: center; min-height: 100vh; margin: 0;
  background: #0f1115; color: #e6e9ef;
}
main { text-align: center; padding: 2rem; }
h1 { font-size: clamp(3rem, 12vw, 6rem); margin: 0; color: #7aa2f7; }
p { color: #a9b1d6; max-width: 38ch; margin: 1rem auto 2rem; }
a { color: #7aa2f7; }
</style>
</head>
<body>
<main>
<h1>404</h1>
<p>The short link <code>{{requested}}</code> does not exist on this site.</p>
<p><a href="{{home}}">Continue to fedpromptly.com</a></p>
</main>
</body>
</html>
"""


class HtmlBuilder:
    """Builds redirect pages, the 404 page and the links manifest."""

    def __init__(self, template_path: str | None = None,
                 site_domain: str = "link.fedpromptly.com") -> None:
        self.site_domain = site_domain.rstrip("/")
        self.template = self._load_template(template_path)

    # ------------------------------------------------------------------ #
    # template handling
    # ------------------------------------------------------------------ #
    def _load_template(self, template_path: str | None) -> str:
        if not template_path:
            return _DEFAULT_TEMPLATE
        try:
            with open(template_path, "r", encoding="utf-8") as handle:
                return handle.read()
        except OSError as exc:
            _LOG.warning(
                "could not read template '%s' (%s); using built-in default",
                template_path, exc,
            )
            return _DEFAULT_TEMPLATE

    def render(self, template: str, values: dict[str, object]) -> str:
        """Fill ``{{ name }}`` placeholders; unknown names are left as-is."""
        def replace(match: re.Match) -> str:
            key = match.group(1)
            return str(values[key]) if key in values else match.group(0)
        return _PLACEHOLDER_RE.sub(replace, template)

    # ------------------------------------------------------------------ #
    # page builders
    # ------------------------------------------------------------------ #
    def build_redirect_page(self, slug: str, url: str) -> str:
        """Render the ``index.html`` that bounces visitors to ``url``."""
        return self.render(self.template, {
            "slug": slug,
            "url": url,
            # json.dumps guarantees a safely escaped JS string literal
            "url_js": json.dumps(url),
            "site_domain": self.site_domain,
            "generated_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%SZ"
            ),
        })

    def build_404_page(self, home_url: str = "https://fedpromptly.com",
                       requested: str = "") -> str:
        """Render the fallback 404 page shown for unknown short links."""
        return self.render(_NOT_FOUND_BODY, {
            "home": home_url,
            "requested": requested or "(unknown)",
        })

    def build_manifest(self, links: dict[str, str]) -> str:
        """Render ``links.json``: slug -> absolute destination URL."""
        manifest = {
            "site": self.site_domain,
            "count": len(links),
            "generated_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "links": {
                slug: url
                for slug, url in sorted(links.items())
            },
        }
        return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
