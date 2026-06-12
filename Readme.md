# Chess Tournament Manager CLI

A Python command-line application for managing chess tournaments. Admins can create multiple tournaments, register players, generate pairings, record results, and produce standings. Players can browse available tournaments, select one, and view pairings, standings, and their own points.

---

## Requirements

- Python 3.14+
- [pip](https://pip.pypa.io/) (included with Python)
- Optional: [Pipenv](https://pipenv.pypa.io/) for dependency management via `Pipfile`

---

## Setup

Choose **one** of the following methods to install dependencies.

### Option A — venv + pip

```powershell
# 1. Clone or navigate to the project folder
cd chess-manager-cli-python

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate         # macOS / Linux

# 4. Install dependencies and the short `chess` command
pip install -r requirements.txt
pip install -e .

# 5. Verify installation
chess whoami
pytest tests/ -v
```

### Option B — Pipenv

```powershell
# 1. Navigate to the project folder
cd chess-manager-cli-python

# 2. Install dependencies from Pipfile (creates virtualenv automatically)
pipenv install --dev
pipenv run pip install -e .

# 3. Run commands inside the Pipenv shell
pipenv shell
chess whoami
pipenv run test
```

---

## Running the Application

Use the short **`chess`** command instead of typing `python main.py` every time.

### Option 1 — `chess` command (recommended)

After setup, run `pip install -e .` once. Then from anywhere (with venv active):

```powershell
chess login admin admin admin123
chess list-tournaments
chess select-tournament T001
chess standings
```

### Option 2 — Launcher scripts (no install needed)

From the project folder:

```powershell
.\chess login admin admin admin123     # PowerShell
.\chess.bat login admin admin admin123 # Command Prompt
```

### Option 3 — Full command (always works)

```powershell
chess <command> [arguments]
```

With Pipenv:

```powershell
pipenv run chess <command> [arguments]
```

---

## Authentication

The CLI uses role-based access. You must log in before using most commands.

| Role   | Access |
|--------|--------|
| Admin  | Create/manage tournaments, players, pairings, results, save/load |
| Player | List tournaments, select a tournament, view pairings/standings/points |

### Default admin (created on first run)

| Field    | Value |
|----------|-------|
| Username | `admin` |
| Password | `admin123` |

```powershell
chess login admin admin admin123
chess whoami
chess logout
```

### Create a new admin

An existing admin must be logged in:

```powershell
chess login admin admin admin123
chess create-admin "Jane Doe" jane mypassword123
```

---

## Multiple tournaments

The app supports **more than one tournament** at a time. Each tournament is stored as its own JSON file. You must know which tournament is active before running player or management commands.

### How it works

1. **`list-tournaments`** — shows every saved tournament and marks the currently selected one.
2. **`select-tournament <id>`** — switches the active tournament (admin and player).
3. All other commands (add player, pairings, standings, etc.) apply to the **selected** tournament.

Tournament files live in `data/tournaments/` (e.g. `T001.json`, `T002.json`). The selected tournament ID is stored in `data/active_tournament.json`.

### Admin — multiple tournaments

```powershell
chess login admin admin admin123

chess create-tournament "Spring Open" T001
chess create-tournament "Winter Cup" T002

chess list-tournaments
chess select-tournament T001
chess add-player Alice 1500

chess select-tournament T002
chess add-player Bob 1400
```

### Player — choose a tournament to view

Players must select a tournament before logging in (or pass `--tournament` at login):

```powershell
chess list-tournaments
chess select-tournament T001
chess login player P001

# Alternative: login and select in one step
chess login player P001 --tournament T001
```

---

## Commands

### Authentication

| Command | Description |
|---------|-------------|
| `login admin <username> <password>` | Log in as admin |
| `login player <player_id> [--tournament ID]` | Log in as player (select tournament first or use `--tournament`) |
| `logout` | End the current session |
| `whoami` | Show logged-in user, role, and active tournament |
| `create-admin <name> <username> <password>` | Create a new admin account (admin only) |

### Tournaments (admin & player)

| Command | Description |
|---------|-------------|
| `list-tournaments` | List all saved tournaments; marks the selected one |
| `select-tournament <id>` | Switch to a different tournament |

### Admin — tournament management

| Command | Description |
|---------|-------------|
| `create-tournament <name> <id>` | Create a new tournament and select it |
| `add-player <name> <rating>` | Register a player in the active tournament (ID like P001) |
| `list-players` | List all players in the active tournament |
| `pair-round` | Generate pairings for the next round |
| `enter-result <match_id> <result>` | Record result: `win`, `loss`, or `draw` (White's perspective) |
| `save [--file path]` | Save active tournament (default: `data/tournaments/<id>.json`) |
| `load [--file path]` | Import a tournament from JSON and select it |

### Admin & player — read-only views

| Command | Description |
|---------|-------------|
| `view-pairings [--round N]` | View pairings for a round (default: current round) |
| `standings` | View the leaderboard (points, then rating tiebreak) |
| `my-points` | View your own points and rank (player only) |

---

## Quick command reference

Activate your virtual environment first:

```powershell
.\venv\Scripts\Activate.ps1
```

### Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Authentication

```powershell
chess login admin admin admin123
chess whoami
chess logout
```

### Create a new admin

```powershell
chess login admin admin admin123
chess create-admin "Jane Doe" jane mypassword123
```

### List and switch tournaments

```powershell
chess list-tournaments
chess select-tournament T001
chess select-tournament T002
```

### Admin workflow

```powershell
chess login admin admin admin123
chess create-tournament "Spring Open" T001
chess create-tournament "Winter Cup" T002
chess list-tournaments
chess select-tournament T001
chess add-player Alice 1500
chess add-player Bob 1400
chess list-players
chess pair-round
chess enter-result M001 win
chess standings
chess save
chess logout
```

### Player workflow

```powershell
chess list-tournaments
chess select-tournament T001
chess login player P001
chess view-pairings
chess view-pairings --round 1
chess standings
chess my-points
chess logout
```

### Individual commands

```powershell
# Tournaments
chess list-tournaments
chess select-tournament T001
chess create-tournament "Spring Open" T001

# Save / load
chess save
chess save --file data/backup.json
chess load --file data/backup.json

# Players
chess add-player Alice 1500
chess list-players

# Rounds & results
chess pair-round
chess enter-result M001 win
chess enter-result M001 loss
chess enter-result M001 draw

# Views
chess standings
chess view-pairings
chess my-points

# Player login with tournament flag
chess login player P001 --tournament T001
```

### Run tests

```powershell
pytest tests/ -v
# or
pipenv run test
```

---

## Console output

The CLI uses [rich](https://github.com/Textualize/rich) for formatted tables and role-based colors:

| Role   | Color theme |
|--------|-------------|
| Admin  | Green |
| Player | White |

Success messages, table borders, and badges use the logged-in role's color.

---

## Data persistence

All data is stored as JSON in the `data/` folder:

| File / folder | Contents |
|---------------|----------|
| `data/tournaments/*.json` | One file per tournament (e.g. `T001.json`, `T002.json`) |
| `data/active_tournament.json` | ID of the currently selected tournament |
| `data/admins.json` | Admin accounts (passwords stored as SHA-256 hashes) |
| `data/session.json` | Current login session (role, player ID, tournament ID) |
| `data/tournament.json` | Legacy single-tournament file (auto-migrated on first run) |

- Tournament data **auto-saves** after admin changes (create, add player, pair round, enter result).
- The **selected tournament auto-loads** on startup for most commands.
- Creating a tournament with a duplicate ID is blocked.

---

## Project structure

```
chess-manager-cli-python/
├── main.py              # CLI entry point (argparse)
├── models/
│   ├── person.py        # Base class
│   ├── admin.py         # Admin (inherits Person)
│   ├── player.py        # Player (inherits Person)
│   ├── tournament.py    # Tournament container
│   └── match.py         # Match between two players
├── utils/
│   ├── auth.py          # Login, sessions, role checks
│   ├── persistence.py   # Multi-tournament JSON save/load
│   ├── pairing.py       # Round pairing logic
│   ├── standings.py     # Leaderboard sorting
│   └── console_theme.py # Role-based rich colors
├── data/
│   ├── tournaments/     # One JSON file per tournament
│   ├── active_tournament.json
│   ├── admins.json
│   └── session.json
├── tests/               # pytest test suite (39 tests)
├── pyproject.toml       # Package config; installs `chess` command
├── chess.bat / chess.ps1 # Short launcher scripts (Windows)
├── Pipfile              # Pipenv dependencies
├── Pipfile.lock         # Locked dependency versions
├── requirements.txt     # pip freeze output
├── commands.md          # Quick command cheat sheet
└── Readme.md
```

---

## OOP design

### Classes

- **Person** — base class with `name` and `person_id`
- **Admin** — inherits Person; manages login credentials
- **Player** — inherits Person; has `rating` and `points`
- **Tournament** — contains players and matches
- **Match** — links two players in a round

### Relationships

- Tournament **contains** Players
- Tournament **contains** Matches
- Match **links** two Players

---

## Pairing rules

1. **Round 1** — players paired by rating (highest vs highest available opponent).
2. **Later rounds** — paired by points, then rating as tiebreak.
3. **Rematches** — avoided when possible; allowed if no other pairing exists.
4. All results in the current round must be entered before pairing the next round.

### Scoring

| Result | Points |
|--------|--------|
| Win    | 1.0    |
| Draw   | 0.5    |
| Loss   | 0.0    |

---

## Testing

The project includes **39 unit tests** covering models, pairing, standings, persistence, auth, CLI commands, console theming, and multi-tournament support.

```powershell
# Using venv
pytest tests/ -v

# Using Pipenv
pipenv run test
```

### Test files

| File | What it tests |
|------|---------------|
| `test_player.py` | Point updates after win/draw/loss |
| `test_pairing.py` | Round 1 by rating, later rounds by points |
| `test_standings.py` | Leaderboard sort and tiebreak |
| `test_persistence.py` | JSON save/load, multi-tournament list and selection |
| `test_auth.py` | Admin/player login and password hashing |
| `test_main_cli.py` | argparse parser, command handlers, tournament switching |
| `test_console_theme.py` | Role-based rich output |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [rich](https://pypi.org/project/rich/) | Formatted CLI tables and colored output |
| [pytest](https://pypi.org/project/pytest/) | Unit testing (dev dependency) |

Managed via `Pipfile` (Pipenv) and `requirements.txt` (pip).

---

## Features

- Multiple tournaments with list and select
- Player registration with unique IDs per tournament
- Swiss-style pairing system
- Match result entry with automatic point updates
- Standings generation with rating tiebreak
- JSON persistence with safe load/save
- Admin and player login with role-based access
- Role-colored CLI output (green admin, white player)
