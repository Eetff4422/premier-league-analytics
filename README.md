# ⚽ Premier League Analytics

> Interactive analytics dashboard for English Premier League data, with automated Word report generation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Built with Dash](https://img.shields.io/badge/built%20with-Dash-119DFF.svg)](https://dash.plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](tests/)

A clean-architecture Python application that loads historical Premier League match data, computes team statistics and season standings, and lets users explore everything through an interactive Plotly/Dash dashboard — or export a fully formatted Word report in one click.

---

## ✨ Features

- 📊 **Interactive dashboard** — season standings, goals timelines, head-to-head comparisons
- 📄 **One-click Word report** — ready-to-share `.docx` with embedded charts and tables
- 🧱 **Clean Architecture** — domain / application / infrastructure / presentation layers
- ✅ **Tested** — pytest suite covering entities and use cases
- 🌍 **100% open data** — built on free public datasets from football-data.co.uk

---

## 🖼️ Preview

```
┌─────────────────────────────────────────────────────┐
│  Premier League Analytics                 Season ▾  │
├─────────────────────────────────────────────────────┤
│                                                      │
│   Standings           Goals Over Time                │
│   ┌──────────┐        ┌──────────────┐              │
│   │ 1. Man C │        │     ╱╲       │              │
│   │ 2. Arsnl │        │    ╱  ╲_╱╲   │              │
│   │ 3. Liv   │        │ ╱╲╱        ╲ │              │
│   │ ...      │        │╱            ╲│              │
│   └──────────┘        └──────────────┘              │
│                                                      │
│   [ Compare two teams ▾ ]  [ 📄 Export Word ]       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

*(Add real screenshots in `/assets` once you run it.)*

---

## 🚀 Quickstart

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/premier-league-analytics.git
cd premier-league-analytics

# 2. Install
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Download the data (free, public, ~5 MB)
python scripts/download_data.py

# 4. Launch the dashboard
python main.py
```

Open http://127.0.0.1:8050 in your browser.

---

## 🏗️ Project Structure

```
premier-league-analytics/
│
├── data/                      # CSV match data (gitignored)
├── reports/                   # Generated Word reports (gitignored)
├── assets/                    # Screenshots and logos
│
├── src/
│   ├── domain/                # Core business entities — no external dependencies
│   │   └── entities.py        # Match, Team, SeasonStanding
│   │
│   ├── application/           # Use cases — orchestrate the business logic
│   │   └── use_cases.py       # AnalyzeSeason, CompareTeams, GenerateReport
│   │
│   ├── infrastructure/        # Adapters to the outside world
│   │   ├── csv_reader.py      # Load match data from CSV
│   │   ├── chart_renderer.py  # Build Plotly figures
│   │   └── word_exporter.py   # Generate .docx reports with python-docx
│   │
│   └── presentation/          # Dash app + callbacks
│       ├── app.py
│       └── callbacks.py
│
├── scripts/
│   └── download_data.py       # Fetch CSVs from football-data.co.uk
│
├── tests/                     # pytest test suite
│   ├── test_entities.py
│   └── test_use_cases.py
│
├── main.py                    # Entry point — launches the Dash server
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

The dependency rule is **one-way**: `presentation → application → domain` and `infrastructure → application → domain`. The `domain` layer knows about nothing else — which makes it trivial to test and easy to reason about.

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Data | Pandas, football-data.co.uk CSVs |
| Visualization | Plotly |
| Dashboard | Dash |
| Report generation | python-docx |
| Testing | pytest |
| Architecture | Clean Architecture (Uncle Bob) |

---

## 📊 Data Source

All data comes from [football-data.co.uk](https://www.football-data.co.uk/englandm.php) — a free, public archive of historical football match results dating back to 1993. No API key or scraping required. See `scripts/download_data.py` for the exact URLs used.

---

## 🗺️ Roadmap

- [ ] Add xG (expected goals) data from Understat
- [ ] Season-over-season trend comparison
- [ ] Player-level stats (when FBref scraping is added)
- [ ] Deploy a live demo on Render / Fly.io
- [ ] Multi-league support (La Liga, Serie A, Ligue 1)

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 👤 About

Built by **Franklin Essono** — data analyst / developer focused on turning messy operational data into tools that people actually use.

- 📧 essono@et.esiea.fr
- 💼 [LinkedIn](https://linkedin.com/in/franklin-essono)
