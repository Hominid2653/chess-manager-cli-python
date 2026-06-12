"""Match between two players in a round."""


class Match:
    """Single game with optional result."""

    def __init__(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        round_num: int,
        result: str | None = None,
    ):
        self.match_id = match_id
        self.player1_id = player1_id  # White
        self.player2_id = player2_id  # Black
        self.round_num = round_num
        self.result = result  # win, loss, or draw (from White's view)

    @property
    def is_complete(self) -> bool:
        """Return True if a result has been recorded."""
        return self.result is not None

    def to_dict(self) -> dict:
        """Convert match data to a dictionary for JSON storage."""
        return {
            "match_id": self.match_id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "round_num": self.round_num,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """Create a Match instance from saved JSON data."""
        return cls(
            match_id=data["match_id"],
            player1_id=data["player1_id"],
            player2_id=data["player2_id"],
            round_num=data["round_num"],
            result=data.get("result"),
        )
