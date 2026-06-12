"""Tests for saving and loading tournament JSON files."""

from pathlib import Path

import pytest

from models.tournament import Tournament
from utils.persistence import (
    save_tournament,
    load_tournament_from_path,
    load_tournament_by_id,
    list_tournament_summaries,
    set_active_tournament_id,
    get_active_tournament_id,
    load_active_tournament,
    tournament_exists,
)


def test_save_and_load_tournament(tournament_storage):
    tournament = Tournament("Spring Open", "T001")
    tournament.add_player("Alice", 1500)
    tournament.add_player("Bob", 1400)

    save_tournament(tournament)
    loaded = load_tournament_by_id("T001")

    assert loaded is not None
    assert loaded.name == "Spring Open"
    assert len(loaded.players) == 2
    assert loaded.players[0].name == "Alice"


def test_load_missing_file_returns_none(tournament_storage):
    assert load_tournament_from_path(tournament_storage["legacy_file"]) is None


def test_load_invalid_json_raises(tournament_storage):
    bad_file = tournament_storage["dir"] / "bad.json"
    bad_file.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_tournament_from_path(bad_file)


def test_list_multiple_tournaments(tournament_storage):
    t1 = Tournament("Spring Open", "T001")
    t2 = Tournament("Winter Cup", "T002")
    save_tournament(t1)
    save_tournament(t2)

    summaries = list_tournament_summaries()
    ids = {item["tournament_id"] for item in summaries}

    assert ids == {"T001", "T002"}
    assert all("name" in item for item in summaries)


def test_active_tournament_selection(tournament_storage):
    tournament = Tournament("Spring Open", "T001")
    save_tournament(tournament)
    set_active_tournament_id("T001")

    assert get_active_tournament_id() == "T001"
    loaded = load_active_tournament()
    assert loaded is not None
    assert loaded.tournament_id == "T001"


def test_tournament_exists(tournament_storage):
    assert not tournament_exists("T999")
    save_tournament(Tournament("Open", "T001"))
    assert tournament_exists("T001")
