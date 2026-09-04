"""Packages the generated tree into an upload-ready ZIP.

The ZIP layout mirrors ``output/`` exactly (``.htaccess`` at the root of
the archive), so it can be extracted straight into InfinityFree's
``htdocs`` — or uploaded unzipped via the control panel's uploader.
"""

import os
import zipfile

from src.utils.logger import get_logger

_LOG = get_logger("generator.zip")

_EXCLUDE_NAMES = {".keep", ".DS_Store", "Thumbs.db", "desktop.ini"}
_EXCLUDE_SUFFIXES = (".log", ".tmp", ".swp")


def _is_excluded(name: str) -> bool:
    return name in _EXCLUDE_NAMES or name.endswith(_EXCLUDE_SUFFIXES)


class ZipPackager:
    """Creates ``links.zip`` from a directory tree."""

    def __init__(self, source_dir: str = "output",
                 zip_path: str = "links.zip") -> None:
        self.source_dir = source_dir
        self.zip_path = zip_path

    def package(self, clean_first: bool = False) -> tuple[str, int]:
        """Zip the tree; return ``(zip_path, file_count)``.

        ``clean_first`` removes an existing ZIP so failures never leave a
        half-written archive lying around.
        """
        if not os.path.isdir(self.source_dir):
            raise FileNotFoundError(
                f"nothing to package: '{self.source_dir}' does not exist — "
                "run the generator first"
            )
        if clean_first and os.path.exists(self.zip_path):
            os.remove(self.zip_path)
            _LOG.debug("removed stale %s", self.zip_path)

        directory = os.path.dirname(os.path.abspath(self.zip_path))
        os.makedirs(directory, exist_ok=True)

        count = 0
        with zipfile.ZipFile(self.zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for root, dirs, files in os.walk(self.source_dir):
                # keep the archive layout deterministic
                dirs.sort()
                for name in sorted(files):
                    if _is_excluded(name):
                        continue
                    absolute = os.path.join(root, name)
                    relative = os.path.relpath(absolute, self.source_dir)
                    archive.write(absolute, relative)
                    count += 1

        if count == 0:
            _LOG.warning("packaged 0 files — is output/ empty?")
        else:
            size_kb = os.path.getsize(self.zip_path) / 1024
            _LOG.info("packaged %d file(s) into %s (%.1f KiB)",
                      count, self.zip_path, size_kb)
        return self.zip_path, count

    def package_generated(self, clean_first: bool = True) -> tuple[str, int]:
        """Convenience wrapper used by the CLI after a build."""
        return self.package(clean_first=clean_first)
