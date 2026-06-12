"""Shared pytest fixtures for CLI and auth tests."""

from pathlib import Path

import pytest

from utils.auth import clear_session


@pytest.fixture(autouse=True)
def isolate_auth_files(tmp_path: Path, monkeypatch):
    """Use temp auth files for every test so sessions never leak."""
    admins_file = tmp_path / "admins.json"
    session_file = tmp_path / "session.json"
    monkeypatch.setattr("utils.auth.ADMINS_PATH", admins_file)
    monkeypatch.setattr("utils.auth.SESSION_PATH", session_file)
    clear_session()
    yield
    clear_session()


@pytest.fixture
def tournament_file(tmp_path: Path, monkeypatch):
    """Point tournament JSON to a temp file."""
    path = tmp_path / "tournament.json"
    monkeypatch.setattr("utils.persistence.DEFAULT_DATA_PATH", path)
    return path
