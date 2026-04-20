"""Tests for the application layer — use cases."""

from datetime import date

import pytest

from src.domain.entities import Match
from src.application.use_cases import (
    compute_standings,
    build_team_timeline,
    compute_head_to_head,
)


@pytest.fixture
def mini_season():
    """A 4-team round-robin half-season."""
    return [
        Match(date(2024, 8, 17), "Arsenal", "Wolves", 2, 0),
        Match(date(2024, 8, 24), "Chelsea", "Man City", 0, 2),
        Match(date(2024, 9, 1), "Arsenal", "Chelsea", 1, 1),
        Match(date(2024, 9, 14), "Man City", "Wolves", 3, 1),
        Match(date(2024, 9, 21), "Arsenal", "Man City", 0, 1),
        Match(date(2024, 9, 28), "Chelsea", "Wolves", 2, 2),
    ]


class TestComputeStandings:

    def test_all_teams_appear(self, mini_season):
        standing = compute_standings("2024/25", mini_season)
        teams = {r.team for r in standing.rows}
        assert teams == {"Arsenal", "Wolves", "Chelsea", "Man City"}

    def test_games_played_count(self, mini_season):
        standing = compute_standings("2024/25", mini_season)
        arsenal = standing.find("Arsenal")
        assert arsenal.played == 3

    def test_leader_is_correct(self, mini_season):
        """Man City should lead: 3 wins, 6 points in 3 games."""
        standing = compute_standings("2024/25", mini_season)
        assert standing.rows[0].team == "Man City"
        assert standing.rows[0].points == 9

    def test_total_goals_conserved(self, mini_season):
        """Sum of goals_for across all teams = sum of goals_against."""
        standing = compute_standings("2024/25", mini_season)
        total_scored = sum(r.goals_for for r in standing.rows)
        total_conceded = sum(r.goals_against for r in standing.rows)
        assert total_scored == total_conceded


class TestBuildTeamTimeline:

    def test_timeline_has_right_length(self, mini_season):
        tl = build_team_timeline("Arsenal", mini_season)
        assert len(tl.matchdays) == 3
        assert len(tl.cumulative_points) == 3

    def test_cumulative_points_are_monotonic(self, mini_season):
        tl = build_team_timeline("Arsenal", mini_season)
        for i in range(1, len(tl.cumulative_points)):
            assert tl.cumulative_points[i] >= tl.cumulative_points[i - 1]

    def test_empty_timeline_for_unknown_team(self, mini_season):
        tl = build_team_timeline("Tottenham", mini_season)
        assert tl.matchdays == []
        assert tl.cumulative_points == []


class TestHeadToHead:

    def test_single_meeting(self, mini_season):
        h2h = compute_head_to_head("Arsenal", "Wolves", mini_season)
        assert h2h.meetings == 1
        assert h2h.a_wins == 1
        assert h2h.b_wins == 0
        assert h2h.draws == 0

    def test_draw_between_teams(self, mini_season):
        h2h = compute_head_to_head("Arsenal", "Chelsea", mini_season)
        assert h2h.meetings == 1
        assert h2h.draws == 1

    def test_no_meetings_returns_zeros(self, mini_season):
        h2h = compute_head_to_head("Arsenal", "Tottenham", mini_season)
        assert h2h.meetings == 0
        assert h2h.a_wins == h2h.b_wins == h2h.draws == 0

    def test_h2h_goals_sum(self, mini_season):
        h2h = compute_head_to_head("Arsenal", "Chelsea", mini_season)
        # 1-1 draw: Arsenal 1, Chelsea 1
        assert h2h.a_goals == 1
        assert h2h.b_goals == 1
