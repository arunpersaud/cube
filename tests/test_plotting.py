import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from cube.plotting import generate_default_figures


class DummyAx:
    def __init__(self):
        self.plot_called = False
        self.step_called = False

    def plot(self, *args, **kwargs):
        self.plot_called = True

    def step(self, *args, **kwargs):
        self.step_called = True

    def grid(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass

    def set_xlabel(self, *args, **kwargs):
        pass

    def set_ylabel(self, *args, **kwargs):
        pass

    def set_title(self, *args, **kwargs):
        pass


class DummyFig:
    def tight_layout(self):
        pass


def _series_frame():
    return pd.DataFrame(
        {
            "time_ms": [1000, 1200, 900, 1300, 1250],
            "datetime": pd.date_range("2024-01-01", periods=5, freq="min"),
        }
    )


def test_generate_default_figures_datetime(monkeypatch):
    frame = _series_frame()
    dummy_ax = DummyAx()

    monkeypatch.setattr(plt, "subplots", lambda *_, **__: (DummyFig(), dummy_ax))

    calls = []

    def fake_show():
        calls.append(True)

    monkeypatch.setattr(plt, "show", fake_show)

    generate_default_figures(frame, axis="datetime")
    assert dummy_ax.plot_called
    assert not dummy_ax.step_called
    assert calls


def test_generate_default_figures_solve(monkeypatch):
    frame = _series_frame()
    dummy_ax = DummyAx()

    monkeypatch.setattr(plt, "subplots", lambda *_, **__: (DummyFig(), dummy_ax))
    monkeypatch.setattr(plt, "show", lambda: None)

    generate_default_figures(frame, axis="solve")
    assert dummy_ax.step_called
    assert dummy_ax.plot_called
