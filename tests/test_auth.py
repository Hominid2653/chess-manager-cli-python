"""Tests for admin/player authentication and session management."""

import json
from pathlib import Path

import pytest

from models.admin import Admin
from models.tournament import Tournament
from utils.auth import (
    authenticate_admin,
    create_admin,
    login_admin,
    login_player,
    clear_session,
    get_session,
    is_admin,
    is_player,
    save_admins,
    ADMINS_PATH,
    SESSION_PATH,
)


@pytest.fixture(autouse=True)
def isolate_auth_files(tmp_path: Path, monkeypatch):
    """Redirect auth file paths to a temp directory for each test."""
    admins_file = tmp_path / "admins.json"
    session_file = tmp_path / "session.json"
    monkeypatch.setattr("utils.auth.ADMINS_PATH", admins_file)
    monkeypatch.setattr("utils.auth.SESSION_PATH", session_file)
    yield
    clear_session()


def test_admin_login_and_session():
    """Admin credentials should create a persisted admin session."""
    admin = create_admin("Chief", "chief", "secret")
    logged_in = login_admin("chief", "secret")

    assert logged_in.username == "chief"
    assert is_admin()
    session = get_session()
    assert session["role"] == "admin"
    assert session["username"] == "chief"


def test_invalid_admin_login_raises():
    """Wrong credentials should raise ValueError."""
    create_admin("Chief", "chief", "secret")
    with pytest.raises(ValueError):
        login_admin("chief", "wrong")


def test_player_login(tmp_path):
    """Player login should bind the session to a tournament player ID."""
    tournament = Tournament("Open", "T001")
    tournament.add_player("Alice", 1500)

    login_player("P001", tournament)

    assert is_player()
    assert get_session()["player_id"] == "P001"


def test_admin_password_hashing():
    """Password hashing should be deterministic and verifiable."""
    hashed = Admin.hash_password("test")
    admin = Admin("A", "A001", "user", hashed)
    assert admin.verify_password("test")
    assert not admin.verify_password("nope")
