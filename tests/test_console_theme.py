"""Tests for role-based rich console styling."""

from io import StringIO

import pytest
from rich.console import Console

import utils.console_theme as theme
from utils.auth import login_admin, create_admin, login_player, clear_session
from models.tournament import Tournament


@pytest.fixture
def capture_console(monkeypatch):
    """Capture rich console output in a string buffer."""
    output = StringIO()
    test_console = Console(file=output, force_terminal=True, width=120)
    monkeypatch.setattr(theme, "console", test_console)
    return output


def test_role_badge_admin():
    badge = theme.role_badge("admin")
    assert "ADMIN" in badge
    assert "green" in badge


def test_role_badge_player():
    badge = theme.role_badge("player")
    assert "PLAYER" in badge
    assert "white" in badge


def test_role_badge_no_role():
    assert theme.role_badge() == ""


def test_make_table_admin_styles():
    table = theme.make_table("Standings", role="admin")
    assert table.border_style == theme.ADMIN_STYLE
    assert "green" in table.title


def test_make_table_player_styles():
    table = theme.make_table("Pairings", role="player")
    assert table.border_style == theme.PLAYER_STYLE
    assert "white" in table.title


def test_id_column_style_by_role():
    assert theme.id_column_style("admin") == theme.ADMIN_ACCENT
    assert theme.id_column_style("player") == theme.PLAYER_ACCENT
    assert theme.id_column_style() == "white"


def test_print_success_admin(capture_console):
    theme.print_success("Tournament created.", role="admin")
    text = capture_console.getvalue()
    assert "ADMIN" in text
    assert "Tournament created." in text


def test_print_success_player(capture_console):
    theme.print_success("Logged in.", role="player")
    text = capture_console.getvalue()
    assert "PLAYER" in text
    assert "Logged in." in text


def test_print_error(capture_console):
    theme.print_error("Access denied.")
    text = capture_console.getvalue()
    assert "Error:" in text
    assert "Access denied." in text


def test_print_warning(capture_console):
    theme.print_warning("No players yet.")
    assert "No players yet." in capture_console.getvalue()


def test_resolve_role_from_session(monkeypatch):
    create_admin("Admin", "boss", "secret")
    login_admin("boss", "secret")
    assert theme._resolve_role() == "admin"
    clear_session()

    tournament = Tournament("Open", "T001")
    tournament.add_player("Alice", 1500)
    login_player("P001", tournament, "T001")
    assert theme._resolve_role() == "player"
