"""Tests for the domain layer."""

from datetime import date

import pytest

from src.domain.entities import Match, MatchResult, TeamStats, SeasonStanding


@pytest.fixture
def home_win():
    return Match(date(2024, 8, 17), "Arsenal", "Wolves", 2, 0)


@pytest.fixture
def away_win():
    return Match(date(2024, 8, 24), "Chelsea", "Man City", 0, 2)


@pytest.fixture
def draw():
    return Match(date(2024, 9, 1), "Liverpool", "Newcastle", 1, 1)


class TestMatch:

    def test_home_win_result(self, home_win):
        assert home_win.result == MatchResult.HOME_WIN

    def test_away_win_result(self, away_win):
        assert away_win.result == MatchResult.AWAY_WIN

    def test_draw_result(self, draw):
        assert draw.result == MatchResult.DRAW

    def test_total_goals(self, home_win):
        assert home_win.total_goals == 2

    def test_involves_home_team(self, home_win):
        assert home_win.involves("Arsenal") is True

    def test_involves_away_team(self, home_win):
        assert home_win.involves("Wolves") is True

    def test_does_not_involve_other_team(self, home_win):
        assert home_win.involves("Chelsea") is False


class TestTeamStats:

    def test_new_team_has_zero_points(self):
        stats = TeamStats(team="Arsenal")
        assert stats.points == 0
        assert stats.played == 0

    def test_apply_home_win(self, home_win):
        stats = TeamStats(team="Arsenal")
        stats.apply_match(home_win)
        assert stats.played == 1
        assert stats.won == 1
        assert stats.points == 3
        assert stats.goals_for == 2
        assert stats.goals_against == 0

    def test_apply_away_loss(self, home_win):
        stats = TeamStats(team="Wolves")
        stats.apply_match(home_win)
        assert stats.played == 1
        assert stats.lost == 1
        assert stats.points == 0
        assert stats.goals_for == 0
        assert stats.goals_against == 2

    def test_apply_draw(self, draw):
        a = TeamStats(team="Liverpool")
        b = TeamStats(team="Newcastle")
        a.apply_match(draw)
        b.apply_match(draw)
        assert a.points == 1
        assert b.points == 1
        assert a.drawn == 1

    def test_goal_difference(self, home_win):
        stats = TeamStats(team="Arsenal")
        stats.apply_match(home_win)
        assert stats.goal_difference == 2

    def test_apply_match_rejects_uninvolved_team(self, home_win):
        stats = TeamStats(team="Chelsea")
        with pytest.raises(ValueError):
            stats.apply_match(home_win)


class TestSeasonStanding:

    def test_empty_standing(self):
        s = SeasonStanding(season="2024/25")
        assert s.top() == []
        assert s.find("Arsenal") is None
        assert s.position_of("Arsenal") is None

    def test_position_of(self):
        a = TeamStats(team="Arsenal", played=1, won=1, goals_for=2)
        b = TeamStats(team="Wolves", played=1, lost=1, goals_against=2)
        s = SeasonStanding(season="2024/25", rows=[a, b])
        assert s.position_of("Arsenal") == 1
        assert s.position_of("Wolves") == 2
        assert s.position_of("Nobody") is None
