"""Handle login, logout, and role-based access."""

import json
from pathlib import Path

from models.admin import Admin

ADMINS_PATH = Path(__file__).resolve().parent.parent / "data" / "admins.json"
SESSION_PATH = Path(__file__).resolve().parent.parent / "data" / "session.json"

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def _ensure_data_dir() -> None:
    """Create the data folder if it does not exist."""
    ADMINS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_admins() -> list[Admin]:
    """Load all admin accounts from disk."""
    _ensure_data_dir()
    try:
        with open(ADMINS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return [Admin.from_dict(a) for a in data.get("admins", [])]
    except FileNotFoundError:
        return []


def save_admins(admins: list[Admin]) -> None:
    """Save all admin accounts to disk."""
    _ensure_data_dir()
    with open(ADMINS_PATH, "w", encoding="utf-8") as f:
        json.dump({"admins": [a.to_dict() for a in admins]}, f, indent=2)


def ensure_default_admin() -> Admin:
    """Create a default admin account on first run."""
    admins = load_admins()
    if admins:
        return admins[0]

    default = Admin(
        name="Tournament Admin",
        admin_id="A001",
        username=DEFAULT_ADMIN_USERNAME,
        password_hash=Admin.hash_password(DEFAULT_ADMIN_PASSWORD),
    )
    save_admins([default])
    return default


def create_admin(name: str, username: str, password: str) -> Admin:
    """Register a new admin with a unique username."""
    admins = load_admins()
    if any(a.username == username for a in admins):
        raise ValueError(f"Username '{username}' is already taken.")

    admin_id = f"A{len(admins) + 1:03d}"
    admin = Admin(
        name=name,
        admin_id=admin_id,
        username=username,
        password_hash=Admin.hash_password(password),
    )
    admins.append(admin)
    save_admins(admins)
    return admin


def authenticate_admin(username: str, password: str) -> Admin | None:
    """Verify admin username and password. Returns the admin if valid."""
    ensure_default_admin()
    for admin in load_admins():
        if admin.username == username and admin.verify_password(password):
            return admin
    return None


def get_session() -> dict | None:
    """Get the current login session, or None if logged out."""
    try:
        with open(SESSION_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_session(session: dict) -> None:
    """Save the current login session to disk."""
    _ensure_data_dir()
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)


def clear_session() -> None:
    """Log out by removing the session file."""
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()


def login_admin(username: str, password: str) -> Admin:
    """Log in as admin and save the session."""
    admin = authenticate_admin(username, password)
    if admin is None:
        raise ValueError("Invalid admin username or password.")

    save_session({
        "role": "admin",
        "username": admin.username,
        "name": admin.name,
        "person_id": admin.person_id,
    })
    return admin


def login_player(player_id: str, tournament, tournament_id: str) -> None:
    """Log in as a player for a specific tournament."""
    player = tournament.get_player(player_id)
    if player is None:
        raise ValueError(
            f"Player '{player_id}' not found in tournament '{tournament_id}'."
        )

    save_session({
        "role": "player",
        "player_id": player.person_id,
        "name": player.name,
        "tournament_id": tournament_id,
    })


def is_admin() -> bool:
    """Return True if the current session is an admin."""
    session = get_session()
    return session is not None and session.get("role") == "admin"


def is_player() -> bool:
    """Return True if the current session is a player."""
    session = get_session()
    return session is not None and session.get("role") == "player"


def get_logged_in_player_id() -> str | None:
    """Return the player ID of the logged-in player, or None."""
    session = get_session()
    if session and session.get("role") == "player":
        return session.get("player_id")
    return None


def get_session_tournament_id() -> str | None:
    """Return the tournament ID tied to the current player session."""
    session = get_session()
    if session:
        return session.get("tournament_id")
    return None
