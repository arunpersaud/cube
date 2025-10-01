"""Plotting helpers built on matplotlib."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import apply_time_features
from .storage import read_parquet


def generate_default_figures(dataset: Path | pd.DataFrame, axis: str = "datetime") -> None:
    """Render interactive plots for cube solves."""

    frame = read_parquet(dataset) if isinstance(dataset, Path) else dataset.copy()
    frame = apply_time_features(frame)
    if frame.empty:
        print("No solves to plot.")
        return

    _plot_timeseries(frame, axis=axis)
    plt.show()


def _plot_timeseries(frame: pd.DataFrame, axis: str) -> None:
    axis = axis.lower()
    if axis not in {"datetime", "solve"}:
        raise ValueError("axis must be 'datetime' or 'solve'")

    series = frame.get("time_s", pd.Series(dtype=float))
    ao5 = frame.get("ao5_s")
    ao12 = frame.get("ao12_s")

    fig, ax = plt.subplots(figsize=(10, 4))

    if axis == "datetime" and "datetime" in frame:
        x = frame["datetime"]
    else:
        x = pd.RangeIndex(start=0, stop=len(series))

    if not series.empty:
        if axis == "solve":
            ax.step(x, series, where="mid", linewidth=1.5, label="Solve (s)")
        else:
            ax.plot(x, series, marker="o", linestyle="-", linewidth=1, markersize=3, label="Solve (s)")

        if ao5 is not None and not ao5.isna().all():
            ax.plot(x, ao5, color="tab:orange", linewidth=2, label="Ao5")
        if ao12 is not None and not ao12.isna().all():
            ax.plot(x, ao12, color="tab:green", linewidth=2, label="Ao12")

    ax.set_xlabel("Solve" if axis == "solve" else "Datetime")
    ax.set_ylabel("Seconds")
    ax.set_title("Solve durations")
    ax.grid(True, linestyle=":", linewidth=0.5)
    if not series.empty:
        ax.legend()

    fig.tight_layout()
