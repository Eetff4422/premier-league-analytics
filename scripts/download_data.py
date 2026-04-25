"""
Download historical Premier League match data from football-data.co.uk.

The site hosts free CSVs at URLs like:
    https://www.football-data.co.uk/mmz4281/2324/E0.csv   (season 2023/24)
    https://www.football-data.co.uk/mmz4281/2425/E0.csv   (season 2024/25)

We save them locally as data/E0_<season>.csv so the app can enumerate them.
"""

from __future__ import annotations
from pathlib import Path
import sys

import requests


BASE_URL = "https://www.football-data.co.uk/mmz4281"
# Last few completed seasons
SEASONS = ["2021/22", "2022/23", "2023/24", "2024/25"]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _season_code(season_label: str) -> str:
    """'2023/24' -> '2324'"""
    left, right = season_label.split("/")
    return f"{left[-2:]}{right}"


def download(season_label: str) -> Path:
    code = _season_code(season_label)
    url = f"{BASE_URL}/{code}/E0.csv"
    out_path = DATA_DIR / f"E0_{code}.csv"

    print(f"  → Fetching {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    out_path.write_bytes(resp.content)
    print(f"  ✓ Saved {out_path.name} ({len(resp.content) // 1024} KB)")
    return out_path


def main() -> int:
    DATA_DIR.mkdir(exist_ok=True)
    print(f"Downloading {len(SEASONS)} Premier League seasons into {DATA_DIR}/")
    print()

    for s in SEASONS:
        try:
            download(s)
        except requests.RequestException as exc:
            print(f"  Failed to download {s}: {exc}", file=sys.stderr)

    print()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
