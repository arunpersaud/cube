import pandas as pd
import pytest

from cube.analysis import compute_summary


def test_compute_summary_with_data():
    frame = pd.DataFrame({"time_ms": [1000, 1500, 900, 1200, 1100, 1300, 1400]})
    summary, stats_frame = compute_summary(frame)
    assert summary["solves"] == 7
    assert summary["best_s"] == 0.9
    assert round(summary["mean_s"], 2) == 1.2
    assert summary["ao5_s"] is not None
    assert summary["ao5_s"] == pytest.approx(1.2, rel=1e-6)
    assert stats_frame["ao5_s"].iloc[-1] == pytest.approx(1.2, rel=1e-6)
    assert summary["ao12_s"] is None
    assert "ao5_s" in stats_frame.columns


def test_compute_summary_empty():
    summary, stats_frame = compute_summary(pd.DataFrame())
    assert summary == {'solves': 0, 'mean_s': 0.0, 'best_s': 0.0, 'ao5_s': None, 'ao12_s': None}
    assert stats_frame.empty
