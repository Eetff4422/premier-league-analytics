"""
Dash app — the presentation layer.

Wires up the UI layout, loads data through the infrastructure layer,
and delegates computations to the use cases.
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime

from dash import Dash, html, dcc, Input, Output, State, dash_table, no_update

from src.application.use_cases import (
    compute_standings,
    build_team_timeline,
    compute_head_to_head,
)
from src.infrastructure.csv_reader import (
    load_matches,
    list_available_seasons,
    season_label_to_filename,
)
from src.infrastructure.chart_renderer import (
    render_standings_bar,
    render_points_timeline,
    render_goals_scatter,
    render_head_to_head,
)
from src.infrastructure.word_exporter import generate_season_report


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"


def create_app() -> Dash:
    """Build and return the Dash application."""
    app = Dash(__name__, title="Premier League Analytics")
    app.layout = _build_layout()
    _register_callbacks(app)
    return app


# ──────────────────────────────────────────────────────────────
# Layout
# ──────────────────────────────────────────────────────────────

STYLES = {
    "app": {
        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, Arial, sans-serif",
        "background": "#F6F6F8",
        "minHeight": "100vh",
        "color": "#1F2937",
    },
    "header": {
        "background": "#37003C",
        "color": "#FFFFFF",
        "padding": "20px 40px",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "space-between",
        "borderBottom": "4px solid #00FF87",
    },
    "brand": {"fontSize": "22px", "fontWeight": "700", "letterSpacing": "-0.5px"},
    "main": {"padding": "24px 40px", "maxWidth": "1400px", "margin": "0 auto"},
    "controls": {
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
        "gap": "12px",
        "background": "#FFFFFF",
        "padding": "16px",
        "borderRadius": "8px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
        "marginBottom": "20px",
    },
    "card": {
        "background": "#FFFFFF",
        "padding": "16px",
        "borderRadius": "8px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
        "marginBottom": "20px",
    },
    "label": {
        "fontSize": "11px",
        "fontWeight": "600",
        "textTransform": "uppercase",
        "letterSpacing": "0.8px",
        "color": "#6B7280",
        "marginBottom": "4px",
        "display": "block",
    },
    "btn_primary": {
        "background": "#37003C",
        "color": "#FFFFFF",
        "border": "none",
        "padding": "10px 20px",
        "borderRadius": "6px",
        "fontWeight": "600",
        "cursor": "pointer",
        "fontSize": "13px",
    },
}


def _build_layout():
    seasons = list_available_seasons(DATA_DIR)
    default_season = seasons[-1] if seasons else None

    return html.Div(style=STYLES["app"], children=[
        # ── Header ──
        html.Div(style=STYLES["header"], children=[
            html.Div("⚽ Premier League Analytics", style=STYLES["brand"]),
            html.Div("by Franklin Essono", style={"fontSize": "13px", "opacity": 0.7}),
        ]),

        # ── Main ──
        html.Div(style=STYLES["main"], children=[

            # Control bar
            html.Div(style=STYLES["controls"], children=[
                html.Div([
                    html.Label("Season", style=STYLES["label"]),
                    dcc.Dropdown(
                        id="season-dropdown",
                        options=[{"label": s, "value": s} for s in seasons] or
                                [{"label": "No data — run scripts/download_data.py", "value": ""}],
                        value=default_season,
                        clearable=False,
                    ),
                ]),
                html.Div([
                    html.Label("Team A", style=STYLES["label"]),
                    dcc.Dropdown(id="team-a-dropdown", clearable=False),
                ]),
                html.Div([
                    html.Label("Team B (compare)", style=STYLES["label"]),
                    dcc.Dropdown(id="team-b-dropdown", clearable=True,
                                 placeholder="Optional"),
                ]),
                html.Div(style={"display": "flex", "alignItems": "flex-end"}, children=[
                    html.Button("📄 Export Word report", id="export-btn",
                                style=STYLES["btn_primary"]),
                ]),
            ]),

            # Export feedback
            html.Div(id="export-status", style={"marginBottom": "20px"}),

            # Standings card
            html.Div(style=STYLES["card"], children=[
                dcc.Graph(id="standings-chart"),
            ]),

            # Timeline card
            html.Div(style=STYLES["card"], children=[
                dcc.Graph(id="timeline-chart"),
            ]),

            # Per-team goals card
            html.Div(style=STYLES["card"], children=[
                dcc.Graph(id="goals-chart"),
            ]),

            # Head-to-head card (only shown when both teams selected)
            html.Div(style=STYLES["card"], children=[
                dcc.Graph(id="h2h-chart"),
            ]),

            # Standings table card
            html.Div(style=STYLES["card"], children=[
                html.H3("Full standings", style={"marginTop": 0, "color": "#37003C"}),
                html.Div(id="standings-table"),
            ]),
        ]),
    ])


# ──────────────────────────────────────────────────────────────
# Callbacks
# ──────────────────────────────────────────────────────────────

def _register_callbacks(app: Dash) -> None:

    @app.callback(
        Output("team-a-dropdown", "options"),
        Output("team-a-dropdown", "value"),
        Output("team-b-dropdown", "options"),
        Input("season-dropdown", "value"),
    )
    def _populate_teams(season):
        if not season:
            return [], None, []
        filename = season_label_to_filename(season)
        matches = load_matches(DATA_DIR / filename)
        teams = sorted({m.home_team for m in matches} | {m.away_team for m in matches})
        options = [{"label": t, "value": t} for t in teams]
        default_a = teams[0] if teams else None
        return options, default_a, options

    @app.callback(
        Output("standings-chart", "figure"),
        Output("timeline-chart", "figure"),
        Output("goals-chart", "figure"),
        Output("h2h-chart", "figure"),
        Output("standings-table", "children"),
        Input("season-dropdown", "value"),
        Input("team-a-dropdown", "value"),
        Input("team-b-dropdown", "value"),
    )
    def _update_charts(season, team_a, team_b):
        import plotly.graph_objects as go

        empty = go.Figure().update_layout(
            title="Select a season to begin",
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        )
        if not season or not team_a:
            return empty, empty, empty, empty, "No data loaded."

        filename = season_label_to_filename(season)
        matches = load_matches(DATA_DIR / filename)
        standing = compute_standings(season, matches)

        # Timelines
        timelines = [build_team_timeline(team_a, matches)]
        if team_b and team_b != team_a:
            timelines.append(build_team_timeline(team_b, matches))

        timeline_fig = render_points_timeline(timelines)
        standings_fig = render_standings_bar(standing)
        goals_fig = render_goals_scatter(timelines[0])

        if team_b and team_b != team_a:
            h2h = compute_head_to_head(team_a, team_b, matches)
            h2h_fig = render_head_to_head(h2h)
        else:
            h2h_fig = go.Figure().update_layout(
                title="Select Team B to see the head-to-head",
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
            )

        # Standings table
        table = dash_table.DataTable(
            data=[
                {
                    "#": i,
                    "Team": r.team,
                    "P": r.played, "W": r.won, "D": r.drawn, "L": r.lost,
                    "GF": r.goals_for, "GA": r.goals_against,
                    "GD": f"{r.goal_difference:+d}",
                    "Pts": r.points,
                }
                for i, r in enumerate(standing.rows, start=1)
            ],
            columns=[{"name": c, "id": c} for c in ["#", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]],
            style_header={"backgroundColor": "#37003C", "color": "white",
                          "fontWeight": "600", "fontSize": "12px"},
            style_cell={"padding": "8px", "fontSize": "12px",
                        "fontFamily": "Inter, Arial, sans-serif"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#FAFAFA"},
            ],
        )

        return standings_fig, timeline_fig, goals_fig, h2h_fig, table

    @app.callback(
        Output("export-status", "children"),
        Input("export-btn", "n_clicks"),
        State("season-dropdown", "value"),
        prevent_initial_call=True,
    )
    def _export_report(n_clicks, season):
        if not season:
            return no_update

        filename = season_label_to_filename(season)
        matches = load_matches(DATA_DIR / filename)
        standing = compute_standings(season, matches)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"premier_league_{season.replace('/', '-')}_{ts}.docx"
        out_path = REPORTS_DIR / out_name
        generate_season_report(standing, out_path)

        return html.Div(
            f"✅ Report saved: reports/{out_name}",
            style={"padding": "12px", "background": "#D1FAE5",
                   "border": "1px solid #00BD5C", "borderRadius": "6px",
                   "color": "#064E3B", "fontSize": "13px", "fontWeight": "500"},
        )
