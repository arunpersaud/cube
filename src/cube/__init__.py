"""Core package for Rubik's cube session analytics."""

from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover - metadata only used at runtime
    __version__ = version("cube")
except PackageNotFoundError:  # pragma: no cover - during local dev without install
    __version__ = "0.0.0"

