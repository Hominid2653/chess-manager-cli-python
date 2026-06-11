class Match:
    def __init__(
        self,
        match_id: str,
        player1_id: str,
        player2_id: str,
        round_num: int,
        result: str | None = None,
    ):
        self.match_id = match_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.round_num = round_num
        self.result = result

    @property
    def is_complete(self) -> bool:
        return self.result is not None

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "round_num": self.round_num,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        return cls(
            match_id=data["match_id"],
            player1_id=data["player1_id"],
            player2_id=data["player2_id"],
            round_num=data["round_num"],
            result=data.get("result"),
        )
