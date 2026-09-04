"""Generator package: everything that turns validated links into files.

``folder_creator`` lays out ``output/<slug>/index.html``,
``html_builder`` renders the redirect pages from a template,
and ``zip_packager`` produces the upload-ready ``links.zip``.
"""

from src.generator.folder_creator import FolderCreator
from src.generator.html_builder import HtmlBuilder
from src.generator.zip_packager import ZipPackager

__all__ = ["FolderCreator", "HtmlBuilder", "ZipPackager"]
