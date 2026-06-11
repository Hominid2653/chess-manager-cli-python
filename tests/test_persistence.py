"""Tests for saving and loading tournament JSON files."""

from pathlib import Path

import pytest

from models.tournament import Tournament
from utils.persistence import save_tournament, load_tournament


def test_save_and_load_tournament(tmp_path: Path):
    tournament = Tournament("Spring Open", "T001")
    tournament.add_player("Alice", 1500)
    tournament.add_player("Bob", 1400)

    file_path = tmp_path / "tournament.json"
    save_tournament(tournament, file_path)

    loaded = load_tournament(file_path)
    assert loaded is not None
    assert loaded.name == "Spring Open"
    assert len(loaded.players) == 2
    assert loaded.players[0].name == "Alice"


def test_load_missing_file_returns_none(tmp_path: Path):
    assert load_tournament(tmp_path / "missing.json") is None


def test_load_invalid_json_raises(tmp_path: Path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_tournament(bad_file)
