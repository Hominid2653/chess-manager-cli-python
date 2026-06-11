"""Standings and leaderboard sorting utilities."""

from models.player import Player
from models.tournament import Tournament


def get_standings(tournament: Tournament) -> list[Player]:
    """
    Return players sorted for the leaderboard.

    Primary sort: points (descending).
    Tiebreak: rating (descending).
    """
    return sorted(
        tournament.players,
        key=lambda p: (p.points, p.rating),
        reverse=True,
    )
