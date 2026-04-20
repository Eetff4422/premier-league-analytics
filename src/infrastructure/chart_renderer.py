"""
Plotly chart renderer — turns domain/application objects into Plotly figures.

Keeps all Plotly/chart styling in one place so it can be swapped out or themed centrally.
"""

from __future__ import annotations
from typing import List

import plotly.graph_objects as go

from src.domain.entities import SeasonStanding
from src.application.use_cases import TeamTimeline, HeadToHead


# Shared color palette — consistent across the dashboard and the Word report
PRIMARY = "#37003C"      # Premier League purple
ACCENT = "#00FF87"       # Signature green
ACCENT_DARK = "#04F5FF"
NEUTRAL = "#6B7280"
BG = "#FFFFFF"
GRID = "#EEEEEE"


def _base_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=16, color=PRIMARY)),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(family="Inter, Arial, sans-serif", color="#1F2937"),
        margin=dict(l=50, r=30, t=60, b=50),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )


def render_standings_bar(standing: SeasonStanding, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of the top N teams by points."""
    top = standing.top(top_n)
    top_reversed = list(reversed(top))   # so the #1 appears at the top
    fig = go.Figure(
        data=[
            go.Bar(
                x=[t.points for t in top_reversed],
                y=[t.team for t in top_reversed],
                orientation="h",
                marker=dict(color=PRIMARY, line=dict(color=ACCENT, width=1.5)),
                text=[t.points for t in top_reversed],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Points: %{x}<br>GD: %{customdata}<extra></extra>",
                customdata=[t.goal_difference for t in top_reversed],
            )
        ]
    )
    fig.update_layout(**_base_layout(f"Top {top_n} — {standing.season}"))
    fig.update_layout(xaxis_title="Points", yaxis_title=None, showlegend=False)
    return fig


def render_points_timeline(timelines: List[TeamTimeline]) -> go.Figure:
    """Cumulative points over matchdays for one or more teams."""
    fig = go.Figure()
    palette = [PRIMARY, ACCENT_DARK, "#E90052", "#FFB81C"]

    for i, tl in enumerate(timelines):
        fig.add_trace(
            go.Scatter(
                x=tl.matchdays,
                y=tl.cumulative_points,
                mode="lines+markers",
                name=tl.team,
                line=dict(width=3, color=palette[i % len(palette)]),
                marker=dict(size=6),
                hovertemplate="<b>%{fullData.name}</b><br>MD %{x}: %{y} pts<extra></extra>",
            )
        )

    fig.update_layout(**_base_layout("Cumulative points across the season"))
    fig.update_layout(
        xaxis_title="Matchday",
        yaxis_title="Points",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render_goals_scatter(timeline: TeamTimeline) -> go.Figure:
    """Goals scored vs conceded per matchday for one team."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=timeline.matchdays,
            y=timeline.goals_for_per_match,
            name="Scored",
            marker_color=ACCENT,
        )
    )
    fig.add_trace(
        go.Bar(
            x=timeline.matchdays,
            y=[-g for g in timeline.goals_against_per_match],
            name="Conceded",
            marker_color="#E90052",
        )
    )
    fig.update_layout(**_base_layout(f"{timeline.team} — Goals per matchday"))
    fig.update_layout(
        barmode="relative",
        xaxis_title="Matchday",
        yaxis_title="Goals",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def render_head_to_head(h2h: HeadToHead) -> go.Figure:
    """Pie-style summary of a head-to-head."""
    labels = [f"{h2h.team_a} wins", "Draws", f"{h2h.team_b} wins"]
    values = [h2h.a_wins, h2h.draws, h2h.b_wins]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=[PRIMARY, NEUTRAL, ACCENT_DARK]),
                textinfo="label+value",
            )
        ]
    )
    fig.update_layout(**_base_layout(f"Head-to-head — {h2h.meetings} meetings"))
    return fig
