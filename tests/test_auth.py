"""Tests for admin and player login."""

from pathlib import Path

import pytest

from models.admin import Admin
from models.tournament import Tournament
from utils.auth import (
    create_admin,
    login_admin,
    login_player,
    clear_session,
    get_session,
    is_admin,
    is_player,
)


def test_admin_login_and_session():
    create_admin("Chief", "chief", "secret")
    logged_in = login_admin("chief", "secret")

    assert logged_in.username == "chief"
    assert is_admin()
    session = get_session()
    assert session["role"] == "admin"
    assert session["username"] == "chief"


def test_invalid_admin_login_raises():
    create_admin("Chief", "chief", "secret")
    with pytest.raises(ValueError):
        login_admin("chief", "wrong")


def test_player_login():
    tournament = Tournament("Open", "T001")
    tournament.add_player("Alice", 1500)

    login_player("P001", tournament)

    assert is_player()
    assert get_session()["player_id"] == "P001"


def test_admin_password_hashing():
    hashed = Admin.hash_password("test")
    admin = Admin("A", "A001", "user", hashed)
    assert admin.verify_password("test")
    assert not admin.verify_password("nope")
