# Chess Tournament Manager CLI

A Python command-line application for managing chess tournaments. Admins can register players, create pairings, record results, and generate standings. Players can log in to view pairings, standings, and their own points.

---

## Requirements

- Python 3.14+
- [pip](https://pip.pypa.io/) (included with Python)
- Optional: [Pipenv](https://pipenv.pypa.io/) for dependency management via `Pipfile`

---

## Setup

Choose **one** of the following methods to install dependencies.

### Option A — venv + pip (recommended for beginners)

```powershell
# 1. Clone or navigate to the project folder
cd chess-manager-cli-python

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate         # macOS / Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python main.py whoami
pytest tests/ -v
```

### Option B — Pipenv

```powershell
# 1. Navigate to the project folder
cd chess-manager-cli-python

# 2. Install dependencies from Pipfile (creates virtualenv automatically)
pipenv install --dev

# 3. Run commands inside the Pipenv shell
pipenv shell
python main.py whoami
pipenv run test
```

---

## Running the Application

All commands are run from the project root:

```powershell
python main.py <command> [arguments]
```

With Pipenv:

```powershell
pipenv run python main.py <command> [arguments]
```

---

## Authentication

The CLI uses role-based access. You must log in before using most commands.

| Role   | Access |
|--------|--------|
| Admin  | Full tournament management (create, add players, pairings, results, save/load) |
| Player | Read-only views (pairings, standings, own points) |

### Default admin (created on first run)

| Field    | Value |
|----------|-------|
| Username | `admin` |
| Password | `admin123` |

```powershell
python main.py login admin admin admin123
python main.py whoami
python main.py logout
```

### Player login

Players log in with the ID assigned when the admin registered them (e.g. `P001`):

```powershell
python main.py login player P001
```

### Create a new admin

An existing admin must be logged in:

```powershell
python main.py login admin admin admin123
python main.py create-admin "Jane Doe" jane mypassword123
```

---

## Commands

### Authentication

| Command | Description |
|---------|-------------|
| `login admin <username> <password>` | Log in as admin |
| `login player <player_id> [--tournament ID]` | Log in as player (select tournament first, or pass `--tournament`) |
| `logout` | End the current session |
| `whoami` | Show the logged-in user and role |
| `create-admin <name> <username> <password>` | Create a new admin account (admin only) |

### Tournaments (admin & player)

| Command | Description |
|---------|-------------|
| `list-tournaments` | List all saved tournaments (marks the selected one) |
| `select-tournament <id>` | Switch to another tournament |

### Admin — tournament management

| Command | Description |
|---------|-------------|
| `create-tournament <name> <id>` | Create a new tournament |
| `add-player <name> <rating>` | Register a player (assigns ID like P001) |
| `list-players` | List all players with rating and points |
| `pair-round` | Generate pairings for the next round |
| `enter-result <match_id> <result>` | Record result: `win`, `loss`, or `draw` (White's perspective) |
| `save [--file path]` | Save tournament to JSON (default: `data/tournament.json`) |
| `load [--file path]` | Load tournament from JSON |

### Admin & player — read-only views

| Command | Description |
|---------|-------------|
| `view-pairings [--round N]` | View pairings for a round (default: current round) |
| `standings` | View the leaderboard sorted by points, then rating |
| `my-points` | View your own points and rank (player only) |

---

## Quick command reference

Copy-paste examples for common tasks. Activate your virtual environment first:

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
python main.py login admin admin admin123
python main.py whoami
python main.py logout

python main.py login player P001
python main.py logout
```

### Create a new admin

```powershell
python main.py login admin admin admin123
python main.py create-admin "Jane Doe" jane mypassword123
```

### Admin workflow

```powershell
python main.py login admin admin admin123
python main.py create-tournament "Spring Open" T001
python main.py add-player Alice 1500
python main.py add-player Bob 1400
python main.py list-players
python main.py pair-round
python main.py enter-result M001 win
python main.py standings
python main.py save
python main.py load
python main.py logout
```

### List and switch tournaments

```powershell
python main.py list-tournaments
python main.py select-tournament T001
python main.py select-tournament T002
```

### Player workflow

```powershell
python main.py list-tournaments
python main.py select-tournament T001
python main.py login player P001
# or: python main.py login player P001 --tournament T001
python main.py view-pairings
python main.py view-pairings --round 1
python main.py standings
python main.py my-points
python main.py logout
```

### Individual commands

```powershell
# Tournament
python main.py create-tournament "Spring Open" T001
python main.py save
python main.py save --file data/backup.json
python main.py load
python main.py load --file data/backup.json

# Players
python main.py add-player Alice 1500
python main.py list-players

# Rounds & results
python main.py pair-round
python main.py enter-result M001 win
python main.py enter-result M001 loss
python main.py enter-result M001 draw

# Standings & pairings
python main.py standings
python main.py view-pairings
python main.py my-points
```

### Run tests

```powershell
pytest tests/ -v
```

---

## Console output

The CLI uses [rich](https://github.com/Textualize/rich) for formatted tables and role-based colors:

| Role   | Color theme |
|--------|-------------|
| Admin  | Green |
| Player | White |

---

## Data persistence

All data is stored as JSON in the `data/` folder:

| File | Contents |
|------|----------|
| `data/tournaments/*.json` | One file per tournament (e.g. `T001.json`) |
| `data/active_tournament.json` | Currently selected tournament ID |
| `data/tournament.json` | Legacy single-tournament file (auto-migrated) |
| `data/admins.json` | Admin accounts (passwords stored as SHA-256 hashes) |
| `data/session.json` | Current login session |

Tournament data auto-saves after admin changes (create, add player, pair round, enter result). The tournament auto-loads on startup for most commands.

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
│   ├── persistence.py   # JSON save/load
│   ├── pairing.py       # Round pairing logic
│   ├── standings.py     # Leaderboard sorting
│   └── console_theme.py # Role-based rich colors
├── data/                # JSON storage (auto-created)
├── tests/               # pytest test suite
├── Pipfile              # Pipenv dependencies
├── Pipfile.lock         # Locked dependency versions
├── requirements.txt     # pip freeze output
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

The project includes **37 unit tests** covering models, pairing, standings, persistence, auth, CLI commands, and console theming.

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
| `test_persistence.py` | JSON save/load and error handling |
| `test_auth.py` | Admin/player login and password hashing |
| `test_main_cli.py` | argparse parser and command handlers |
| `test_console_theme.py` | Role-based rich output |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [rich](https://pypi.org/project/rich/) | Formatted CLI tables and colored output |
| [pytest](https://pypi.org/project/pytest/) | Unit testing (dev dependency) |

Managed via `Pipfile` (Pipenv) and `requirements.txt` (pip).

---

## MVP features

- Player registration with unique IDs
- Swiss-style pairing system
- Match result entry with automatic point updates
- Standings generation with rating tiebreak
- JSON persistence with safe load/save
- Admin and player login with role-based access
