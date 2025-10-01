import json
from pathlib import Path

import pandas as pd

from cube import add


_SAMPLE_EXPORT = {
    "session1": [
        [[0, 1234], "R U R' U'", "", 1700000000],
        [[-1, 2345], "L U2 L' U", "note", 1700001000],
    ],
    "properties": {
        "sessionData": json.dumps(
            {
                "1": {"name": "3x3", "opt": {"scrType": "333"}},
            }
        )
    },
}


def test_load_sessions(tmp_path: Path):
    export_path = tmp_path / "export.json"
    export_path.write_text(json.dumps(_SAMPLE_EXPORT), encoding="utf-8")

    frame = add.load_sessions([export_path])
    assert len(frame) == 2
    assert frame["source"].tolist() == ["export.json", "export.json"]
    assert frame["session"].unique().tolist() == ["3x3"]
    assert frame["scramble_type"].dropna().iloc[0] == "333"
    assert frame["time_ms"].tolist() == [1234, 2345]
    assert frame["penalty_ms"].tolist() == [0, 0]
    assert frame["datetime"].notna().all()
    assert frame["ao5_s"].isna().all()
    assert frame["ao12_s"].isna().all()


def test_append_and_dedupe(tmp_path: Path):
    export_path = tmp_path / "export.json"
    export_path.write_text(json.dumps(_SAMPLE_EXPORT), encoding="utf-8")

    new_frame = add.load_sessions([export_path])
    duplicate_frame = add.append_and_dedupe(new_frame, new_frame)
    assert len(duplicate_frame) == 2
    assert "ao5_s" in duplicate_frame.columns

    extra_export = {
        **_SAMPLE_EXPORT,
        "session1": _SAMPLE_EXPORT["session1"] + [[[0, 3456], "F", "", 1700002000]],
    }
    extra_path = tmp_path / "extra.json"
    extra_path.write_text(json.dumps(extra_export), encoding="utf-8")

    more_frame = add.load_sessions([extra_path])
    merged = add.append_and_dedupe(new_frame, more_frame)
    assert len(merged) == 3
    assert merged["ao5_s"].iloc[-1] is not None or pd.isna(merged["ao5_s"].iloc[-1])


def test_load_real_file():
    sample_path = Path(__file__).parent / "data" / "cstimer_20250826_192544.txt"
    frame = add.load_sessions([sample_path])
    assert not frame.empty
    assert frame["source"].unique().tolist() == ["cstimer_20250826_192544.txt"]
    assert frame["session"].notna().all()
    assert frame["time_ms"].gt(0).any()
    assert "ao5_s" in frame.columns


def test_append_different_scramble_type_kept():
    base = pd.DataFrame(
        {
            "scramble": ["R U R' U"],
            "time_ms": [1000],
            "scramble_type": ["333"],
            "penalty_code": [0],
            "penalty_ms": [0],
            "full_time_ms": [1000],
            "session": ["3x3"],
            "session_key": ["session1"],
            "session_number": [1],
            "solve_index": [0],
            "source": ["manual"],
            "utc_timestamp": [1700000000],
            "datetime": pd.to_datetime(["2023-01-01T00:00:00Z"]),
            "notes": [""],
        }
    )

    other = base.copy()
    other["scramble_type"] = ["pll"]
    merged = add.append_and_dedupe(base, other)
    assert len(merged) == 2
    assert "ao5_s" in merged.columns
