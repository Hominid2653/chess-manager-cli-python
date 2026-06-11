"""Sort players for the leaderboard."""

from models.player import Player
from models.tournament import Tournament


def get_standings(tournament: Tournament) -> list[Player]:
    """Return players sorted by points, then rating as a tiebreak."""
    return sorted(
        tournament.players,
        key=lambda p: (p.points, p.rating),
        reverse=True,
    )
