from models.person import Person
"""Player model."""


class Player(Person):
    """A competitor with a rating and tournament score."""

    def __init__(self, name: str, player_id: str, rating: int = 1200, points: float = 0.0):
        super().__init__(name, player_id)
        self.rating = rating
        self.points = points

    def add_result(self, result: str) -> None:
        """Add points based on match outcome: win=1, draw=0.5, loss=0."""
        if result == "win":
            self.points += 1.0
        elif result == "draw":
            self.points += 0.5

    def to_dict(self) -> dict:
        """Convert player data to a dictionary for JSON storage."""
        return {
            **super().to_dict(),
            "player_id": self.person_id,
            "rating": self.rating,
            "points": self.points,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create a Player instance from saved JSON data."""
        return cls(
            name=data["name"],
            player_id=data.get("player_id", data.get("person_id", "")),
            rating=data.get("rating", 1200),
            points=data.get("points", 0.0),
        )
