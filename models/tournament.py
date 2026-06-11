from models.player import Player
from models.match import Match


class Tournament:
    def __init__(self, name: str, tournament_id: str):
        self.name = name
        self.tournament_id = tournament_id
        self.players: list[Player] = []
        self.matches: list[Match] = []
        self.current_round = 0
        self._next_player_num = 1
        self._next_match_num = 1

    def add_player(self, name: str, rating: int) -> Player:
        player_id = f"P{self._next_player_num:03d}"
        self._next_player_num += 1
        player = Player(name=name, player_id=player_id, rating=rating)
        self.players.append(player)
        return player

    def get_player(self, player_id: str) -> Player | None:
        for player in self.players:
            if player.person_id == player_id:
                return player
        return None

    def has_played(self, player1_id: str, player2_id: str) -> bool:
        pair = {player1_id, player2_id}
        for match in self.matches:
            if {match.player1_id, match.player2_id} == pair:
                return True
        return False

    def get_round_matches(self, round_num: int) -> list[Match]:
        return [m for m in self.matches if m.round_num == round_num]

    def add_match(self, player1_id: str, player2_id: str, round_num: int) -> Match:
        match_id = f"M{self._next_match_num:03d}"
        self._next_match_num += 1
        match = Match(match_id, player1_id, player2_id, round_num)
        self.matches.append(match)
        return match

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tournament_id": self.tournament_id,
            "current_round": self.current_round,
            "next_player_num": self._next_player_num,
            "next_match_num": self._next_match_num,
            "players": [p.to_dict() for p in self.players],
            "matches": [m.to_dict() for m in self.matches],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tournament":
        tournament = cls(name=data["name"], tournament_id=data["tournament_id"])
        tournament.current_round = data.get("current_round", 0)
        tournament._next_player_num = data.get("next_player_num", 1)
        tournament._next_match_num = data.get("next_match_num", 1)
        tournament.players = [Player.from_dict(p) for p in data.get("players", [])]
        tournament.matches = [Match.from_dict(m) for m in data.get("matches", [])]
        return tournament
