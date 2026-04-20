"""
Domain entities for Premier League analytics.

Pure Python objects with no external dependencies (no pandas, no Dash, no I/O).
This layer defines *what* a match or a standing is in our problem domain.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List


class MatchResult(str, Enum):
    """Full-time result from the home team's perspective."""
    HOME_WIN = "H"
    DRAW = "D"
    AWAY_WIN = "A"


@dataclass(frozen=True)
class Match:
    """A single football match."""
    match_date: date
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int

    @property
    def result(self) -> MatchResult:
        if self.home_goals > self.away_goals:
            return MatchResult.HOME_WIN
        if self.home_goals < self.away_goals:
            return MatchResult.AWAY_WIN
        return MatchResult.DRAW

    @property
    def total_goals(self) -> int:
        return self.home_goals + self.away_goals

    def involves(self, team: str) -> bool:
        return team in (self.home_team, self.away_team)


@dataclass
class TeamStats:
    """Season-level stats for a single team. Mutable so we can accumulate match-by-match."""
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return self.won * 3 + self.drawn

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def apply_match(self, match: Match) -> None:
        """Update this team's stats with the outcome of `match`. Raises if team not involved."""
        if not match.involves(self.team):
            raise ValueError(f"Team {self.team!r} is not part of this match")

        is_home = match.home_team == self.team
        scored = match.home_goals if is_home else match.away_goals
        conceded = match.away_goals if is_home else match.home_goals

        self.played += 1
        self.goals_for += scored
        self.goals_against += conceded

        if scored > conceded:
            self.won += 1
        elif scored < conceded:
            self.lost += 1
        else:
            self.drawn += 1


@dataclass
class SeasonStanding:
    """Full league standings for a season, sorted by points then goal difference."""
    season: str
    rows: List[TeamStats] = field(default_factory=list)

    def top(self, n: int = 5) -> List[TeamStats]:
        return self.rows[:n]

    def find(self, team: str) -> TeamStats | None:
        return next((r for r in self.rows if r.team == team), None)

    def position_of(self, team: str) -> int | None:
        """1-indexed position of `team` in the standings, or None if missing."""
        for idx, row in enumerate(self.rows, start=1):
            if row.team == team:
                return idx
        return None
