# Cube

Cube is a Python toolkit for collecting, storing, and visualising Rubik's Cube solve
history. It reads raw [cstimer](https://cstimer.net) JSON exports, writes a parquet
backing store for fast analytics, computes summary statistics, and renders exploratory
matplotlib plots. Entries from the json files are deduplicated.

## Quick start

```bash
uv sync --dev          # create the virtualenv and install runtime + pytest
uv run cube add ~/cube/*.txt
uv run cube analyze  # summary + latest 15 solves
uv run cube plot
uv run cube plot --axis=solve
uv run cube info
```

The CLI accepts any number of export files and consolidates them into
a single parquet file stored under your user data directory (per
`platformdirs`). Analysis prints a readable summary plus the latest 15
solves with Ao5/Ao12 values, and plots are rendered interactively
(choose `--axis=solve` for stepped x-axis by solve order) with
Ao5/Ao12 overlays. Run `cube info` at any time to print the resolved
dataset path.

## Development

- `uv add <package>` manages dependencies in `pyproject.toml`
- `uv run pytest` executes the automated test suite
- install [prek](https://prek.j178.dev/) for pre-commit hooks

## Other packages

The cstimer import is based on
[scramble-history](https://github.com/purarue/scramble-history), which
does most of what I wanted (and more), but did not seem to have a
parquet file backend for a single storage.

