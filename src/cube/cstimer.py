"""Utilities for parsing CSTimer export files."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Optional


@dataclass(frozen=True)
class SessionSolve:
    source: str
    session_number: int
    session_name: str
    session_key: str
    scramble_type: Optional[str]
    scramble: str
    notes: str
    penalty_code: int
    time_ms: int
    utc_timestamp: int
    solve_index: int

    @property
    def datetime(self) -> Optional[datetime]:
        if not self.utc_timestamp:
            return None
        try:
            return datetime.fromtimestamp(int(self.utc_timestamp), tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None

    @property
    def penalty_ms(self) -> int:
        return 0 if self.penalty_code == -1 else self.penalty_code

    @property
    def elapsed_ms(self) -> int:
        return (self.time_ms or 0) + self.penalty_ms


def parse_file(path: Path) -> Iterator[SessionSolve]:
    """Yield solves from a CSTimer export file."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    session_info = _parse_session_metadata(raw)

    for session_number, metadata in session_info.items():
        session_key = f"session{session_number}"
        solves = raw.get(session_key, [])
        session_name = metadata.get("name", session_key)
        scramble_type = (metadata.get("opt") or {}).get("scrType")

        for index, entry in enumerate(solves):
            parsed = _parse_solve(entry)
            if parsed is None:
                continue
            yield SessionSolve(
                source=path.name,
                session_number=int(session_number),
                session_name=session_name,
                session_key=session_key,
                scramble_type=scramble_type,
                scramble=parsed["scramble"],
                notes=parsed["notes"],
                penalty_code=parsed["penalty_code"],
                time_ms=parsed["time_ms"],
                utc_timestamp=parsed["utc_timestamp"],
                solve_index=index,
            )


def iter_unique_solves(paths: Iterable[Path]) -> Iterator[SessionSolve]:
    """Iterate solves across files, dropping duplicates."""

    seen: set[tuple[str, int, str | None]] = set()
    for path in paths:
        for solve in parse_file(path):
            key = (solve.scramble, solve.time_ms, solve.scramble_type)
            if key in seen:
                continue
            seen.add(key)
            yield solve


def _parse_session_metadata(raw: dict) -> dict:
    props = raw.get("properties") or {}
    session_data = props.get("sessionData")
    if not isinstance(session_data, str):
        return {}
    try:
        return json.loads(session_data)
    except json.JSONDecodeError:
        return {}


def _parse_solve(entry) -> Optional[dict]:
    try:
        timing, scramble, notes, timestamp = entry
        penalty_code, time_ms = timing
    except (ValueError, TypeError):
        return None

    return {
        "scramble": (scramble or "").strip(),
        "notes": notes or "",
        "penalty_code": int(penalty_code),
        "time_ms": int(time_ms),
        "utc_timestamp": int(timestamp),
    }
