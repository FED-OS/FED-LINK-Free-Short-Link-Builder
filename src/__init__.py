"""FED-LINk: InfinityFree Short Link Builder.

A small, dependency-light toolkit that turns a simple links file
(JSON, YAML or CSV) into a ready-to-upload bundle for InfinityFree:

  - one folder per short link, each with a redirecting ``index.html``
  - an Apache ``.htaccess`` with 301 ``Redirect`` rules
  - a 404 fallback page
  - everything packaged into a single ZIP you can upload to ``htdocs``

The package is intentionally flat: ``main`` drives, ``parsers`` read,
``validators`` check, ``generator`` builds, ``utils`` support.
"""

__title__ = "infinityfree-shortener-builder"
__version__ = "1.1.0"
__all__ = ["generator", "parsers", "validators", "utils"]
