"""Persistence helpers for solve datasets."""

import platformdirs
from pathlib import Path

import pandas as pd

_DIRS = platformdirs.PlatformDirs(appname="cube", appauthor=False)


def default_data_dir() -> Path:
    """Return the platform-specific data directory for this application."""

    return Path(_DIRS.user_data_dir)


def default_dataset_path() -> Path:
    """Return the canonical parquet path for stored solves."""

    return default_data_dir() / "solves.parquet"


def write_parquet(frame: pd.DataFrame, destination: Path | None = None) -> Path:
    """Persist the dataframe to the parquet store, creating parent directories."""

    destination = destination or default_dataset_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(destination, index=False)
    return destination


def read_parquet(source: Path | None = None) -> pd.DataFrame:
    """Load the parquet dataset into a dataframe."""

    source = source or default_dataset_path()
    return pd.read_parquet(source)
