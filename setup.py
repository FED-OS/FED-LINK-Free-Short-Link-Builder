"""setup.py for FED-LINk (infinityfree-shortener-builder).

The real packaging metadata lives in pyproject.toml (PEP 621). This file
exists for compatibility with tooling that still expects setup.py —
`pip install -e .`, older build frontends, and a few IDE integrations.
It does nothing but delegate.

Usage (equivalent modern form in parentheses):
    python setup.py --help          (pip install -e .)
    python -m pip install -e .      (editable install of the generator)
"""

from setuptools import setup

setup()
