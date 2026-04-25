"""
Use cases: the orchestration layer.
This module contains the main application logic, orchestrating the domain entities to implement the use cases of the application.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Dict

from src.domain.entities import Match, TeamStats, SeasonStanding


def compute_standings(season: str, matches: Iterable[Match]) -> SeasonStanding:
    """
    Build the league standings from a list of matches.
    Teams are ranked by points (desc), then goal difference (desc), then goals scored (desc).
    """
    stats_by_team: Dict[str, TeamStats] = {}

    for m in matches:
        for team in (m.home_team, m.away_team):
            if team not in stats_by_team:
                stats_by_team[team] = TeamStats(team=team)
            stats_by_team[team].apply_match(m)

    ranked = sorted(
        stats_by_team.values(),
        key=lambda s: (s.points, s.goal_difference, s.goals_for),
        reverse=True,
    )
    return SeasonStanding(season=season, rows=ranked)


@dataclass
class TeamTimeline:
    """Cumulative points per matchday for one team."""
    team: str
    matchdays: List[int]
    cumulative_points: List[int]
    goals_for_per_match: List[int]
    goals_against_per_match: List[int]


def build_team_timeline(team: str, matches: Iterable[Match]) -> TeamTimeline:
    """Return cumulative points and per-match goals for `team`, in chronological order."""
    team_matches = sorted(
        (m for m in matches if m.involves(team)),
        key=lambda m: m.match_date,
    )

    matchdays: List[int] = []
    cumulative: List[int] = []
    goals_for: List[int] = []
    goals_against: List[int] = []

    running_points = 0
    for i, m in enumerate(team_matches, start=1):
        is_home = m.home_team == team
        scored = m.home_goals if is_home else m.away_goals
        conceded = m.away_goals if is_home else m.home_goals

        if scored > conceded:
            running_points += 3
        elif scored == conceded:
            running_points += 1

        matchdays.append(i)
        cumulative.append(running_points)
        goals_for.append(scored)
        goals_against.append(conceded)

    return TeamTimeline(
        team=team,
        matchdays=matchdays,
        cumulative_points=cumulative,
        goals_for_per_match=goals_for,
        goals_against_per_match=goals_against,
    )


@dataclass
class HeadToHead:
    """Aggregate comparison between two teams across a set of matches."""
    team_a: str
    team_b: str
    meetings: int
    a_wins: int
    b_wins: int
    draws: int
    a_goals: int
    b_goals: int


def compute_head_to_head(team_a: str, team_b: str, matches: Iterable[Match]) -> HeadToHead:
    """Compute a head-to-head summary for two teams."""
    a_wins = b_wins = draws = 0
    a_goals = b_goals = 0
    meetings = 0

    for m in matches:
        if not (m.involves(team_a) and m.involves(team_b)):
            continue
        meetings += 1

        if m.home_team == team_a:
            a_score, b_score = m.home_goals, m.away_goals
        else:
            a_score, b_score = m.away_goals, m.home_goals

        a_goals += a_score
        b_goals += b_score

        if a_score > b_score:
            a_wins += 1
        elif a_score < b_score:
            b_wins += 1
        else:
            draws += 1

    return HeadToHead(
        team_a=team_a,
        team_b=team_b,
        meetings=meetings,
        a_wins=a_wins,
        b_wins=b_wins,
        draws=draws,
        a_goals=a_goals,
        b_goals=b_goals,
    )
