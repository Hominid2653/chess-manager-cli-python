"""Utility modules for persistence, pairing, standings, and authentication."""

from utils.persistence import save_tournament, load_tournament, DEFAULT_DATA_PATH
from utils.pairing import generate_pairings
from utils.standings import get_standings
from utils.auth import (
    login_admin,
    login_player,
    clear_session,
    get_session,
    is_admin,
    is_player,
    create_admin,
    ensure_default_admin,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
)

__all__ = [
    "save_tournament",
    "load_tournament",
    "DEFAULT_DATA_PATH",
    "generate_pairings",
    "get_standings",
    "login_admin",
    "login_player",
    "clear_session",
    "get_session",
    "is_admin",
    "is_player",
    "create_admin",
    "ensure_default_admin",
    "DEFAULT_ADMIN_USERNAME",
    "DEFAULT_ADMIN_PASSWORD",
]
