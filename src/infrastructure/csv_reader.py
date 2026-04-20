"""
CSV reader — parses football-data.co.uk match CSVs into domain Match objects.

CSV schema (relevant columns):
    Date:  'DD/MM/YYYY' or 'DD/MM/YY'
    HomeTeam, AwayTeam: strings
    FTHG, FTAG: full-time home/away goals (integers)

Any row with missing required fields is silently skipped.
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from src.domain.entities import Match


REQUIRED_COLUMNS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]


def _parse_date(raw: str) -> datetime:
    """football-data.co.uk uses two formats depending on the era — try both."""
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    raise ValueError(f"Unrecognized date format: {raw!r}")


def load_matches(csv_path: str | Path) -> List[Match]:
    """Load a football-data.co.uk CSV and return a list of Match objects."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(path, encoding="latin-1")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV {path.name} is missing required columns: {missing}")

    df = df[REQUIRED_COLUMNS].dropna()

    matches: List[Match] = []
    for _, row in df.iterrows():
        try:
            match_date = _parse_date(str(row["Date"])).date()
            matches.append(
                Match(
                    match_date=match_date,
                    home_team=str(row["HomeTeam"]).strip(),
                    away_team=str(row["AwayTeam"]).strip(),
                    home_goals=int(row["FTHG"]),
                    away_goals=int(row["FTAG"]),
                )
            )
        except (ValueError, TypeError):
            # skip malformed rows
            continue

    return matches


def list_available_seasons(data_dir: str | Path) -> List[str]:
    """Return the list of available seasons inferred from filenames like `E0_2324.csv`."""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []
    seasons = []
    for f in sorted(data_dir.glob("E0_*.csv")):
        # filename pattern: E0_2324.csv -> season label "2023/24"
        stem = f.stem.split("_")[-1]
        if len(stem) == 4 and stem.isdigit():
            label = f"20{stem[:2]}/{stem[2:]}"
            seasons.append(label)
    return seasons


def season_label_to_filename(season_label: str) -> str:
    """'2023/24' -> 'E0_2324.csv'"""
    left, right = season_label.split("/")
    return f"E0_{left[-2:]}{right}.csv"
