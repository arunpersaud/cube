"""Statistical helpers for cube solve datasets."""

from pathlib import Path
from typing import Mapping

import pandas as pd

from .metrics import apply_time_features, summary_stats
from .storage import read_parquet

_SORT_COLUMNS = ("datetime", "session", "solve_index")


def compute_summary(dataset: Path | pd.DataFrame) -> tuple[Mapping[str, float | None], pd.DataFrame]:
    """Compute headline metrics and return a stats-annotated dataframe."""

    frame = read_parquet(dataset) if isinstance(dataset, Path) else dataset.copy()
    frame = _sort_frame(frame)
    stats_frame = apply_time_features(frame)
    times = stats_frame["time_s"].dropna()

    if times.empty:
        summary: Mapping[str, float | None] = {
            "solves": 0,
            "mean_s": 0.0,
            "best_s": 0.0,
            "ao5_s": None,
            "ao12_s": None,
        }
        return summary, stats_frame

    summary = {
        "solves": int(times.count()),
        "mean_s": float(times.mean()),
        "best_s": float(times.min()),
        "ao5_s": float(stats_frame["ao5_s"].dropna().iloc[-1]) if not stats_frame["ao5_s"].dropna().empty else None,
        "ao12_s": float(stats_frame["ao12_s"].dropna().iloc[-1]) if not stats_frame["ao12_s"].dropna().empty else None,
    }

    return summary, stats_frame


def _sort_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()

    sort_columns = [column for column in _SORT_COLUMNS if column in frame.columns]
    if sort_columns:
        frame = frame.sort_values(sort_columns, na_position="last")
    return frame.reset_index(drop=True)
