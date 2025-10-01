"""Command line entry-points for the cube analytics toolkit.

Usage:
  cube add <inputs>...
  cube analyze
  cube plot [--axis=<axis>]
  cube info
  cube (-h | --help | --version)

Options:
  --axis=<axis>  Plot x-axis; "datetime" (default) or "solve".
"""

from pathlib import Path
from typing import Sequence

import pandas as pd
from docopt import docopt

from . import __version__, analysis, storage


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI flags and delegate to the appropriate workflow."""

    args = docopt(
        __doc__,
        argv=argv,
        version=f"cube {__version__}",
    )

    dataset = storage.default_dataset_path()

    if args["add"]:
        from . import add

        inputs = [Path(path) for path in args["<inputs>"]]
        solves = add.load_sessions(inputs)
        existing = storage.read_parquet(dataset) if dataset.exists() else None
        combined = add.append_and_dedupe(existing, solves)
        storage.write_parquet(combined, dataset)
        print(f"Dataset stored at: {dataset}")
        return 0

    if args["analyze"]:
        summary, stats_frame = analysis.compute_summary(dataset)
        stats = analysis.summary_stats(stats_frame)
        _print_summary(summary, stats)
        _print_recent(stats_frame)
        return 0

    if args["plot"]:
        from . import plotting

        axis = args.get("--axis") or "datetime"
        plotting.generate_default_figures(dataset, axis=axis)
        return 0

    if args["info"]:
        print(f"Dataset stored at: {dataset}")
        return 0

    raise RuntimeError("Unhandled command")


def _print_summary(summary: dict[str, float | None], stats: dict[str, object]) -> None:
    print("Summary:")
    print(f"  Total solves: {summary['solves']}")
    print(f"  Mean: {summary['mean_s']:.2f}s")
    print(f"  Best: {summary['best_s']:.2f}s")

    ao5 = summary.get("ao5_s")
    ao12 = summary.get("ao12_s")
    print(f"  Latest Ao5: {ao5:.2f}s" if ao5 is not None else "  Latest Ao5: n/a")
    print(f"  Latest Ao12: {ao12:.2f}s" if ao12 is not None else "  Latest Ao12: n/a")

    best_time = stats.get("best_time")
    if best_time is not None:
        print(f"  Best single: {best_time:.2f}s ({stats.get('best_time_datetime')})")
    best_ao5 = stats.get("best_ao5")
    if best_ao5 is not None:
        print(f"  Best Ao5: {best_ao5:.2f}s ({stats.get('best_ao5_datetime')})")
    best_ao12 = stats.get("best_ao12")
    if best_ao12 is not None:
        print(f"  Best Ao12: {best_ao12:.2f}s ({stats.get('best_ao12_datetime')})")


def _print_recent(frame: pd.DataFrame, limit: int = 15) -> None:
    if frame.empty:
        print("\nNo solves recorded yet.")
        return

    recent = frame.tail(limit)
    start_index = len(frame) - len(recent) + 1

    print(f"\nLast {len(recent)} solves:")
    header = "  {0:>4}  {1:<20}  {2:>8}  {3:>8}  {4:>8}".format(
        "Idx", "When", "Time", "Ao5", "Ao12"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    def fmt(value: float | None) -> str:
        if value is None or pd.isna(value):
            return "-"
        return f"{value:.2f}"

    for offset, (_, row) in enumerate(recent.iterrows(), start=start_index):
        when = row.get("datetime")
        when_str = str(when)[:20] if pd.notna(when) else "-"
        print(
            "  {0:>4}  {1:<20}  {2:>8}  {3:>8}  {4:>8}".format(
                offset,
                when_str,
                fmt(row.get("time_s")),
                fmt(row.get("ao5_s")),
                fmt(row.get("ao12_s")),
            )
        )
