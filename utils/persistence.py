"""JSON file persistence for tournament data."""

import json
from pathlib import Path

from models.tournament import Tournament

# Default location for the active tournament snapshot.
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tournament.json"


def save_tournament(tournament: Tournament, path: Path | None = None) -> None:
    """Write tournament state to a JSON file, creating parent dirs as needed."""
    file_path = path or DEFAULT_DATA_PATH
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tournament.to_dict(), f, indent=2)


def load_tournament(path: Path | None = None) -> Tournament | None:
    """Load tournament state from JSON; returns None when the file is missing."""
    file_path = path or DEFAULT_DATA_PATH
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return Tournament.from_dict(data)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, KeyError) as exc:
        raise ValueError(f"Failed to load tournament from {file_path}: {exc}") from exc
