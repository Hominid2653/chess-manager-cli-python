"""Match model linking two players in a specific tournament round."""


class Match:
    """A single game between two players, optionally with a recorded result."""

    def __init__(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        round_num: int,
        result: str | None = None,
    ):
        self.match_id = match_id
        # player1_id is treated as White; player2_id as Black in the CLI.
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.round_num = round_num
        # Result is recorded from White's perspective: win, loss, or draw.
        self.result = result

    @property
    def is_complete(self) -> bool:
        """True when a result has been entered for this match."""
        return self.result is not None

    def to_dict(self) -> dict:
        """Serialize match data for tournament JSON persistence."""
        return {
            "match_id": self.match_id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "round_num": self.round_num,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """Rebuild a Match instance from persisted JSON data."""
        return cls(
            match_id=data["match_id"],
            player1_id=data["player1_id"],
            player2_id=data["player2_id"],
            round_num=data["round_num"],
            result=data.get("result"),
        )
