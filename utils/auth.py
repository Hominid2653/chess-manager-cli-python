"""Authentication, session management, and role-based access control."""

import json
from pathlib import Path

from models.admin import Admin

# Paths for persisted admin accounts and the active CLI session.
ADMINS_PATH = Path(__file__).resolve().parent.parent / "data" / "admins.json"
SESSION_PATH = Path(__file__).resolve().parent.parent / "data" / "session.json"

# Default bootstrap credentials created when no admin accounts exist yet.
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def _ensure_data_dir() -> None:
    """Create the data directory if it does not already exist."""
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
    """Persist the full list of admin accounts to disk."""
    _ensure_data_dir()
    with open(ADMINS_PATH, "w", encoding="utf-8") as f:
        json.dump({"admins": [a.to_dict() for a in admins]}, f, indent=2)


def ensure_default_admin() -> Admin:
    """Create a default admin account when none exist (first-run bootstrap)."""
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
    """Register a new admin account with a unique username."""
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
    """Verify admin credentials and return the Admin on success."""
    ensure_default_admin()
    for admin in load_admins():
        if admin.username == username and admin.verify_password(password):
            return admin
    return None


def get_session() -> dict | None:
    """Return the active session dict, or None when logged out."""
    try:
        with open(SESSION_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_session(session: dict) -> None:
    """Write the active session to disk so it survives separate CLI invocations."""
    _ensure_data_dir()
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)


def clear_session() -> None:
    """Remove the session file to log the user out."""
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()


def login_admin(username: str, password: str) -> Admin:
    """Authenticate and start an admin session."""
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


def login_player(player_id: str, tournament) -> None:
    """Authenticate a player by tournament player ID and start a player session."""
    player = tournament.get_player(player_id)
    if player is None:
        raise ValueError(f"Player '{player_id}' not found in the active tournament.")

    save_session({
        "role": "player",
        "player_id": player.person_id,
        "name": player.name,
    })


def is_admin() -> bool:
    """Return True when the current session belongs to an admin."""
    session = get_session()
    return session is not None and session.get("role") == "admin"


def is_player() -> bool:
    """Return True when the current session belongs to a player."""
    session = get_session()
    return session is not None and session.get("role") == "player"


def get_logged_in_player_id() -> str | None:
    """Return the player ID from the active session, if logged in as a player."""
    session = get_session()
    if session and session.get("role") == "player":
        return session.get("player_id")
    return None
