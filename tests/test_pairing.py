"""Tests for round pairing logic."""

from models.tournament import Tournament
from utils.pairing import generate_pairings


def test_round_one_pairs_by_rating():
    tournament = Tournament("Test Open", "T001")
    tournament.add_player("Low", 1200)
    tournament.add_player("High", 1800)
    tournament.add_player("Mid", 1500)
    tournament.add_player("Top", 2000)

    matches = generate_pairings(tournament)

    assert len(matches) == 2
    assert tournament.current_round == 1
    pair_sets = [{m.player1_id, m.player2_id} for m in matches]
    assert {"P002", "P004"} in pair_sets
    assert {"P001", "P003"} in pair_sets


def test_subsequent_round_pairs_by_points():
    tournament = Tournament("Test Open", "T001")
    p1 = tournament.add_player("Alice", 1600)
    p2 = tournament.add_player("Bob", 1500)
    p3 = tournament.add_player("Carol", 1400)
    p4 = tournament.add_player("Dave", 1300)

    generate_pairings(tournament)
    tournament.matches[0].result = "win"
    p1.add_result("win")
    p2.add_result("loss")
    tournament.matches[1].result = "draw"
    p3.add_result("draw")
    p4.add_result("draw")

    matches = generate_pairings(tournament)
    assert tournament.current_round == 2
    assert len(matches) == 2
