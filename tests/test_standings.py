"""Tests for leaderboard sorting by points and rating tiebreak."""

from models.tournament import Tournament
from utils.standings import get_standings


def test_standings_sorted_by_points_then_rating():
    """Players with equal points should be ordered by higher rating first."""
    tournament = Tournament("Test Open", "T001")
    p1 = tournament.add_player("Alice", 1500)
    p2 = tournament.add_player("Bob", 1600)
    p3 = tournament.add_player("Carol", 1700)

    p1.points = 2.0
    p2.points = 2.0
    p3.points = 1.0

    standings = get_standings(tournament)

    assert standings[0].name == "Bob"
    assert standings[1].name == "Alice"
    assert standings[2].name == "Carol"
