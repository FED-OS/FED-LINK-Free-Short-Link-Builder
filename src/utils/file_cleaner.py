"""Directory helpers: creation, cleaning and safe relative paths.

``clean_directory`` is used between builds so deleted links really do
disappear from ``output/`` instead of lingering as stale folders.
"""

import os
import shutil

from src.utils.logger import get_logger

_LOG = get_logger("utils.file_cleaner")
_KEEP_NAME = ".keep"


def ensure_directory(path: str) -> str:
    """Create ``path`` (and parents) if missing; return the absolute path."""
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


def _is_generated(path: str) -> bool:
    """True for files/folders the generator is allowed to remove.

    Anything under version control such as ``.keep`` markers or ``.git``
    directories is preserved. Hidden files created by the OS (``.DS_Store``,
    ``Thumbs.db``) are swept away, since they never belong in a build.
    """
    name = os.path.basename(path)
    if name in {_KEEP_NAME, ".git"}:
        return False
    return True


def clean_directory(path: str, keep: tuple[str, ...] = (_KEEP_NAME,)) -> int:
    """Remove everything inside ``path`` except entries listed in ``keep``.

    Returns the number of top-level entries removed. The directory itself
    is kept (created if missing). Failures are logged, never raised, so a
    partially-locked directory cannot abort an entire build.
    """
    ensure_directory(path)
    removed = 0
    for entry in os.listdir(path):
        if entry in keep:
            continue
        if not _is_generated(os.path.join(path, entry)):
            continue
        target = os.path.join(path, entry)
        try:
            if os.path.isdir(target) and not os.path.islink(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
            removed += 1
            _LOG.debug("removed %s", target)
        except OSError as exc:  # pragma: no cover - platform dependent
            _LOG.warning("could not remove %s (%s)", target, exc)
    return removed


def relative_path(path: str, start: str) -> str:
    """Return ``path`` relative to ``start`` in OS-native form."""
    return os.path.relpath(path, start)
