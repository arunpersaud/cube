"""Helpers for converting raw CSTimer exports into tabular data."""

from pathlib import Path
from typing import Iterable

import pandas as pd

from . import cstimer
from .metrics import apply_time_features


def load_sessions(paths: Iterable[Path]) -> pd.DataFrame:
    """Read CSTimer JSON exports into a normalized dataframe."""

    records = []
    for solve in cstimer.iter_unique_solves(paths):
        records.append(
            {
                "source": solve.source,
                "session": solve.session_name,
                "session_key": solve.session_key,
                "session_number": solve.session_number,
                "solve_index": solve.solve_index,
                "penalty_code": solve.penalty_code,
                "penalty_ms": solve.penalty_ms,
                "time_ms": solve.time_ms,
                "full_time_ms": solve.elapsed_ms,
                "scramble": solve.scramble,
                "notes": solve.notes,
                "utc_timestamp": solve.utc_timestamp,
                "datetime": solve.datetime,
                "scramble_type": solve.scramble_type,
            }
        )

    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        return apply_time_features(frame)

    frame.sort_values(
        ["datetime", "session", "solve_index"], inplace=True, na_position="last"
    )
    frame.reset_index(drop=True, inplace=True)
    return apply_time_features(frame)


def append_and_dedupe(existing: pd.DataFrame | None, new: pd.DataFrame) -> pd.DataFrame:
    """Merge new solves with the existing dataset and drop duplicates."""

    frames = [df for df in (existing, new) if df is not None and not df.empty]
    if not frames:
        return apply_time_features(new)

    combined = pd.concat(frames, ignore_index=True)
    if "penalty_ms" not in combined:
        penalties = combined.get("penalty_code", 0)
        combined["penalty_ms"] = penalties.where(penalties != -1, 0)
    if "full_time_ms" not in combined:
        combined["full_time_ms"] = combined["time_ms"].fillna(0) + combined["penalty_ms"].fillna(0)

    combined.sort_values(
        ["datetime", "session", "solve_index"], inplace=True, na_position="last"
    )
    combined.drop_duplicates(
        subset=["scramble", "time_ms", "scramble_type"], inplace=True, keep="first"
    )
    combined.reset_index(drop=True, inplace=True)
    return apply_time_features(combined)
