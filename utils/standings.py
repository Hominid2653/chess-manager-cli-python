from models.player import Player
from models.tournament import Tournament


def get_standings(tournament: Tournament) -> list[Player]:
    return sorted(
        tournament.players,
        key=lambda p: (p.points, p.rating),
        reverse=True,
    )
