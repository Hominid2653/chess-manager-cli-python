"""Tests for main CLI parser and command handlers."""

import argparse

import pytest

import main
from models.tournament import Tournament
from utils.auth import create_admin, login_admin
from utils.persistence import load_tournament, save_tournament


EXPECTED_COMMANDS = [
    "login",
    "logout",
    "whoami",
    "create-admin",
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


def test_parser_add_player_args():
    args = _parse(["add-player", "Bob", "1400"])
    assert args.name == "Bob"
    assert args.rating == 1400


def test_parser_enter_result_args():
    args = _parse(["enter-result", "M001", "draw"])
    assert args.match_id == "M001"
    assert args.result == "draw"


def test_require_admin_exits_without_session(monkeypatch):
    monkeypatch.setattr(main, "is_admin", lambda: False)
    with pytest.raises(SystemExit):
        main.require_admin()


def test_require_player_exits_without_session(monkeypatch):
    monkeypatch.setattr(main, "is_player", lambda: False)
    with pytest.raises(SystemExit):
        main.require_player()


def test_get_active_tournament_exits_when_empty():
    with pytest.raises(SystemExit):
        main.get_active_tournament()


def test_cmd_create_tournament(tournament_file, monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    monkeypatch.setattr(main, "is_admin", lambda: True)

    args = argparse.Namespace(name="Winter Cup", id="T100")
    main.cmd_create_tournament(args)

    assert main._tournament is not None
    assert main._tournament.name == "Winter Cup"
    assert tournament_file.exists()
    loaded = load_tournament(tournament_file)
    assert loaded.name == "Winter Cup"


def test_cmd_add_player(tournament_file, monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    monkeypatch.setattr(main, "is_admin", lambda: True)

    tournament = Tournament("Open", "T001")
    save_tournament(tournament, tournament_file)
    monkeypatch.setattr(main, "_tournament", tournament)

    args = argparse.Namespace(name="Alice", rating=1600)
    main.cmd_add_player(args)

    assert len(main._tournament.players) == 1
    assert main._tournament.players[0].name == "Alice"


def test_cmd_enter_result_updates_points(tournament_file, monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    monkeypatch.setattr(main, "is_admin", lambda: True)

    tournament = Tournament("Open", "T001")
    p1 = tournament.add_player("Alice", 1500)
    p2 = tournament.add_player("Bob", 1400)
    match = tournament.add_match(p1.person_id, p2.person_id, 1)
    tournament.current_round = 1
    monkeypatch.setattr(main, "_tournament", tournament)

    args = argparse.Namespace(match_id=match.match_id, result="win")
    main.cmd_enter_result(args)

    assert p1.points == 1.0
    assert p2.points == 0.0
    assert match.result == "win"


def test_cmd_login_admin(monkeypatch):
    create_admin("Admin", "boss", "secret")
    args = argparse.Namespace(role="admin", username="boss", password="secret", player_id=None)
    main.cmd_login(args)
    assert main.is_admin()


def test_cmd_login_player(tournament_file, monkeypatch):
    tournament = Tournament("Open", "T001")
    tournament.add_player("Alice", 1500)
    save_tournament(tournament, tournament_file)
    monkeypatch.setattr(main, "_tournament", tournament)

    args = argparse.Namespace(role="player", username="P001", password=None, player_id="P001")
    main.cmd_login(args)
    assert main.is_player()


def test_cmd_logout():
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    main.cmd_logout(argparse.Namespace())
    assert main.get_session() is None
