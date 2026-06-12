"""Tests for main CLI parser and command handlers."""

import argparse

import pytest

import main
from models.tournament import Tournament
from utils.auth import create_admin, login_admin
from utils.persistence import (
    load_tournament_by_id,
    save_tournament,
    set_active_tournament_id,
    get_active_tournament_id,
)


EXPECTED_COMMANDS = [
    "login",
    "logout",
    "whoami",
    "create-admin",
    "list-tournaments",
    "select-tournament",
    "create-tournament",
    "add-player",
    "list-players",
    "pair-round",
    "enter-result",
    "save",
    "load",
    "view-pairings",
    "standings",
    "my-points",
]


@pytest.fixture(autouse=True)
def reset_tournament(monkeypatch):
    """Reset in-memory tournament before each CLI test."""
    monkeypatch.setattr(main, "_tournament", None)
    yield
    monkeypatch.setattr(main, "_tournament", None)


def _parse(argv: list[str]) -> argparse.Namespace:
    return main.build_parser().parse_args(argv)


def test_build_parser_includes_all_commands():
    parser = main.build_parser()
    for command in EXPECTED_COMMANDS:
        args = parser.parse_args([command] + _dummy_args(command))
        assert args.command == command
        assert hasattr(args, "func")


def _dummy_args(command: str) -> list[str]:
    """Minimal valid arguments per command for parser smoke tests."""
    defaults = {
        "login": ["admin", "user", "pass"],
        "logout": [],
        "whoami": [],
        "create-admin": ["Name", "user2", "pass"],
        "list-tournaments": [],
        "select-tournament": ["T001"],
        "create-tournament": ["Open", "T001"],
        "add-player": ["Alice", "1500"],
        "list-players": [],
        "pair-round": [],
        "enter-result": ["M001", "win"],
        "save": [],
        "load": [],
        "view-pairings": [],
        "standings": [],
        "my-points": [],
    }
    return defaults[command]


def test_parser_create_tournament_args():
    args = _parse(["create-tournament", "Spring Open", "T001"])
    assert args.name == "Spring Open"
    assert args.id == "T001"


def test_parser_select_tournament_args():
    args = _parse(["select-tournament", "T002"])
    assert args.tournament_id == "T002"


def test_require_admin_exits_without_session(monkeypatch):
    monkeypatch.setattr(main, "is_admin", lambda: False)
    with pytest.raises(SystemExit):
        main.require_admin()


def test_get_active_tournament_exits_when_empty(tournament_storage, monkeypatch):
    monkeypatch.setattr(main, "_tournament", None)
    monkeypatch.setattr(main, "load_active_tournament", lambda: None)
    with pytest.raises(SystemExit):
        main.get_active_tournament()


def test_cmd_create_tournament(tournament_storage, monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    monkeypatch.setattr(main, "is_admin", lambda: True)

    args = argparse.Namespace(name="Winter Cup", id="T100")
    main.cmd_create_tournament(args)

    assert main._tournament is not None
    assert main._tournament.name == "Winter Cup"
    assert get_active_tournament_id() == "T100"
    loaded = load_tournament_by_id("T100")
    assert loaded.name == "Winter Cup"


def test_cmd_list_and_select_tournament(tournament_storage, monkeypatch):
    monkeypatch.setattr(main, "is_admin", lambda: True)
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")

    save_tournament(Tournament("Open A", "T001"))
    save_tournament(Tournament("Open B", "T002"))

    main.cmd_list_tournaments(argparse.Namespace())
    main.cmd_select_tournament(argparse.Namespace(tournament_id="T002"))

    assert get_active_tournament_id() == "T002"
    assert main._tournament.name == "Open B"


def test_cmd_add_player(tournament_storage, monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    monkeypatch.setattr(main, "is_admin", lambda: True)

    tournament = Tournament("Open", "T001")
    save_tournament(tournament)
    set_active_tournament_id("T001")
    monkeypatch.setattr(main, "_tournament", tournament)

    args = argparse.Namespace(name="Alice", rating=1600)
    main.cmd_add_player(args)

    assert len(main._tournament.players) == 1
    assert main._tournament.players[0].name == "Alice"


def test_cmd_enter_result_updates_points(tournament_storage, monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    monkeypatch.setattr(main, "is_admin", lambda: True)

    tournament = Tournament("Open", "T001")
    p1 = tournament.add_player("Alice", 1500)
    p2 = tournament.add_player("Bob", 1400)
    match = tournament.add_match(p1.person_id, p2.person_id, 1)
    tournament.current_round = 1
    set_active_tournament_id("T001")
    monkeypatch.setattr(main, "_tournament", tournament)

    args = argparse.Namespace(match_id=match.match_id, result="win")
    main.cmd_enter_result(args)

    assert p1.points == 1.0
    assert p2.points == 0.0
    assert match.result == "win"


def test_cmd_login_admin(monkeypatch):
    create_admin("Admin", "boss", "secret")
    args = argparse.Namespace(
        role="admin", username="boss", password="secret",
        player_id=None, tournament_id=None,
    )
    main.cmd_login(args)
    assert main.is_admin()


def test_cmd_login_player(tournament_storage, monkeypatch):
    tournament = Tournament("Open", "T001")
    tournament.add_player("Alice", 1500)
    save_tournament(tournament)
    set_active_tournament_id("T001")
    monkeypatch.setattr(main, "_tournament", tournament)

    args = argparse.Namespace(
        role="player",
        username="P001",
        password=None,
        player_id="P001",
        tournament_id="T001",
    )
    main.cmd_login(args)
    assert main.is_player()


def test_cmd_logout():
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    main.cmd_logout(argparse.Namespace())
    assert main.get_session() is None
