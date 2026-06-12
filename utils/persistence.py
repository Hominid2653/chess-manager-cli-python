"""Save and load tournament data as JSON files."""

import json
from pathlib import Path

from models.tournament import Tournament

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOURNAMENTS_DIR = DATA_DIR / "tournaments"
LEGACY_TOURNAMENT_PATH = DATA_DIR / "tournament.json"
ACTIVE_TOURNAMENT_PATH = DATA_DIR / "active_tournament.json"

# Kept for backwards compatibility in save/load --file usage
DEFAULT_DATA_PATH = LEGACY_TOURNAMENT_PATH


def _ensure_dirs() -> None:
    """Create data and tournaments folders if missing."""
    TOURNAMENTS_DIR.mkdir(parents=True, exist_ok=True)


def tournament_file_path(tournament_id: str) -> Path:
    """Return the JSON file path for a tournament ID."""
    return TOURNAMENTS_DIR / f"{tournament_id}.json"


def migrate_legacy_tournament() -> None:
    """Move a single old tournament.json into the tournaments folder."""
    _ensure_dirs()
    if not LEGACY_TOURNAMENT_PATH.exists():
        return

    try:
        tournament = load_tournament_from_path(LEGACY_TOURNAMENT_PATH)
    except ValueError:
        return

    if tournament is None:
        return

    target = tournament_file_path(tournament.tournament_id)
    if not target.exists():
        save_tournament(tournament, target)

    if get_active_tournament_id() is None:
        set_active_tournament_id(tournament.tournament_id)


def save_tournament(tournament: Tournament, path: Path | None = None) -> None:
    """Write tournament data to a JSON file."""
    _ensure_dirs()
    file_path = path or tournament_file_path(tournament.tournament_id)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tournament.to_dict(), f, indent=2)


def load_tournament_from_path(path: Path) -> Tournament | None:
    """Read tournament data from a specific JSON file path."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return Tournament.from_dict(data)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, KeyError) as exc:
        raise ValueError(f"Failed to load tournament from {path}: {exc}") from exc


def load_tournament_by_id(tournament_id: str) -> Tournament | None:
    """Load a tournament by its ID from the tournaments folder."""
    migrate_legacy_tournament()
    return load_tournament_from_path(tournament_file_path(tournament_id))


def load_active_tournament() -> Tournament | None:
    """Load the currently selected tournament."""
    migrate_legacy_tournament()
    tournament_id = get_active_tournament_id()
    if tournament_id is None:
        return None
    return load_tournament_by_id(tournament_id)


def tournament_exists(tournament_id: str) -> bool:
    """Return True if a tournament file exists for the given ID."""
    migrate_legacy_tournament()
    return tournament_file_path(tournament_id).exists()


def list_tournament_summaries() -> list[dict]:
    """Return summary info for every saved tournament."""
    migrate_legacy_tournament()
    _ensure_dirs()
    summaries = []

    for file_path in sorted(TOURNAMENTS_DIR.glob("*.json")):
        try:
            tournament = load_tournament_from_path(file_path)
        except ValueError:
            continue
        if tournament is None:
            continue

        summaries.append({
            "tournament_id": tournament.tournament_id,
            "name": tournament.name,
            "player_count": len(tournament.players),
            "current_round": tournament.current_round,
        })

    summaries.sort(key=lambda item: item["name"].lower())
    return summaries


def get_active_tournament_id() -> str | None:
    """Return the ID of the currently selected tournament."""
    try:
        with open(ACTIVE_TOURNAMENT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tournament_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def set_active_tournament_id(tournament_id: str) -> None:
    """Set which tournament is currently selected."""
    _ensure_dirs()
    with open(ACTIVE_TOURNAMENT_PATH, "w", encoding="utf-8") as f:
        json.dump({"tournament_id": tournament_id}, f, indent=2)


# Backwards-compatible aliases used by older tests and imports
def load_tournament(path: Path | str | None = None) -> Tournament | None:
    """Load a tournament from a path, ID string, or the active tournament."""
    if isinstance(path, Path):
        return load_tournament_from_path(path)
    if isinstance(path, str):
        return load_tournament_by_id(path)
    return load_active_tournament()
