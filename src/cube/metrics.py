"""Reusable time-series metrics for cube solves."""

import numpy as np
import pandas as pd


def apply_time_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add time-based helper columns (seconds, Ao5, Ao12) to the dataframe."""

    enriched = frame.copy()
    if enriched.empty:
        for column in ("time_s", "ao5_s", "ao12_s"):
            if column not in enriched:
                enriched[column] = pd.Series(dtype=float)
        return enriched

    time_ms = pd.to_numeric(enriched.get("time_ms"), errors="coerce")
    time_s = time_ms / 1000.0
    enriched["time_s"] = time_s
    enriched["ao5_s"] = _rolling_trimmed_mean(time_s, window=5)
    enriched["ao12_s"] = _rolling_trimmed_mean(time_s, window=12)
    return enriched


def summary_stats(frame: pd.DataFrame) -> dict[str, object]:
    stats: dict[str, object] = {}
    if frame.empty or "time_s" not in frame:
        stats.update({"best_time": None, "best_time_idx": None, "best_time_datetime": None})
    else:
        best_idx = frame["time_s"].idxmin()
        stats["best_time"] = float(frame.loc[best_idx, "time_s"])
        stats["best_time_idx"] = int(best_idx)
        stats["best_time_datetime"] = frame.loc[best_idx, "datetime"] if "datetime" in frame.columns else None

    for column, key in (("ao5_s", "best_ao5"), ("ao12_s", "best_ao12")):
        if column not in frame or frame[column].dropna().empty:
            stats[key] = None
            stats[f"{key}_idx"] = None
            stats[f"{key}_datetime"] = None
            continue
        idx = frame[column].dropna().idxmin()
        stats[key] = float(frame.loc[idx, column])
        stats[f"{key}_idx"] = int(idx)
        stats[f"{key}_datetime"] = frame.loc[idx, "datetime"] if "datetime" in frame.columns else None

    return stats


def _rolling_trimmed_mean(series: pd.Series, *, window: int) -> pd.Series:
    if series.empty:
        return pd.Series(index=series.index, dtype=float)

    def _calc(values: np.ndarray) -> float:
        valid = values[~np.isnan(values)]
        if valid.size < window:
            return np.nan
        trimmed = np.sort(valid)
        trimmed = trimmed[1:-1]
        if trimmed.size == 0:
            return np.nan
        return float(trimmed.mean())

    return series.rolling(window=window, min_periods=window).apply(_calc, raw=True)
