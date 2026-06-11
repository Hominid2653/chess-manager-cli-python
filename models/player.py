"""Competitor model with rating, points, and match-result tracking."""

from models.person import Person


class Player(Person):
    """A registered tournament player who can view pairings, standings, and points."""

    def __init__(self, name: str, player_id: str, rating: int = 1200, points: float = 0.0):
        super().__init__(name, player_id)
        self.rating = rating
        self.points = points

    def add_result(self, result: str) -> None:
        """Update points based on a match outcome (win, loss, or draw)."""
        if result == "win":
            self.points += 1.0
        elif result == "draw":
            self.points += 0.5
        # Losses award zero points; no update needed.

    def to_dict(self) -> dict:
        """Serialize player data for tournament JSON persistence."""
        return {
            **super().to_dict(),
            "player_id": self.person_id,
            "rating": self.rating,
            "points": self.points,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Rebuild a Player instance from persisted JSON data."""
        return cls(
            name=data["name"],
            player_id=data.get("player_id", data.get("person_id", "")),
            rating=data.get("rating", 1200),
            points=data.get("points", 0.0),
        )
