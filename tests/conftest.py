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
def tournament_storage(tmp_path: Path, monkeypatch):
    """Point tournament storage to a temp directory."""
    tournaments_dir = tmp_path / "tournaments"
    tournaments_dir.mkdir()
    active_file = tmp_path / "active_tournament.json"
    legacy_file = tmp_path / "tournament.json"

    monkeypatch.setattr("utils.persistence.DATA_DIR", tmp_path)
    monkeypatch.setattr("utils.persistence.TOURNAMENTS_DIR", tournaments_dir)
    monkeypatch.setattr("utils.persistence.ACTIVE_TOURNAMENT_PATH", active_file)
    monkeypatch.setattr("utils.persistence.LEGACY_TOURNAMENT_PATH", legacy_file)
    monkeypatch.setattr("utils.persistence.DEFAULT_DATA_PATH", legacy_file)

    return {
        "dir": tmp_path,
        "tournaments_dir": tournaments_dir,
        "active_file": active_file,
        "legacy_file": legacy_file,
    }


@pytest.fixture
def tournament_file(tournament_storage):
    """Backward-compatible fixture returning a legacy tournament path."""
    return tournament_storage["legacy_file"]
