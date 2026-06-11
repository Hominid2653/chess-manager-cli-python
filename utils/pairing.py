"""Pairing logic for Swiss-style round generation."""

from models.tournament import Tournament
from models.match import Match


def generate_pairings(tournament: Tournament) -> list[Match]:
    """
    Generate pairings for the next round.

    Round 1 pairs by rating (highest vs highest unpaired, etc.).
    Later rounds pair by points, avoiding repeat matchups when possible.
    """
    if len(tournament.players) < 2:
        raise ValueError("Need at least 2 players to generate pairings.")

    # Block new pairings until every match in the current round is finished.
    incomplete = [
        m for m in tournament.get_round_matches(tournament.current_round)
        if not m.is_complete
    ]
    if incomplete:
        raise ValueError(
            f"Round {tournament.current_round} has unfinished matches. "
            "Enter all results before pairing the next round."
        )

    next_round = tournament.current_round + 1

    if next_round == 1:
        # First round: strongest players meet strongest available opponents by rating.
        ordered = sorted(tournament.players, key=lambda p: p.rating, reverse=True)
    else:
        # Subsequent rounds: sort by score, then rating as tiebreak.
        ordered = sorted(
            tournament.players,
            key=lambda p: (p.points, p.rating),
            reverse=True,
        )

    paired_ids: set[str] = set()
    new_matches: list[Match] = []

    for i, player in enumerate(ordered):
        if player.person_id in paired_ids:
            continue

        opponent = _find_opponent(tournament, ordered, i, paired_ids)
        if opponent is None:
            continue

        match = tournament.add_match(player.person_id, opponent.person_id, next_round)
        paired_ids.add(player.person_id)
        paired_ids.add(opponent.person_id)
        new_matches.append(match)

    tournament.current_round = next_round
    return new_matches


def _find_opponent(tournament, ordered, start_index, paired_ids):
    """Pick the best available opponent, preferring players who have not met yet."""
    player = ordered[start_index]

    # First pass: nearest rank opponent without a previous matchup.
    for j in range(start_index + 1, len(ordered)):
        candidate = ordered[j]
        if candidate.person_id in paired_ids:
            continue
        if not tournament.has_played(player.person_id, candidate.person_id):
            return candidate

    # Second pass: allow rematches if no fresh pairing is possible.
    for j in range(start_index + 1, len(ordered)):
        candidate = ordered[j]
        if candidate.person_id not in paired_ids:
            return candidate

    return None
