# Quick command reference

See [Readme.md](Readme.md) for full setup and documentation.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Admin workflow

```powershell
python main.py login admin admin admin123
python main.py create-tournament "Spring Open" T001
python main.py add-player Alice 1500
python main.py add-player Bob 1400
python main.py pair-round
python main.py enter-result M001 win
python main.py standings
python main.py logout
```

## List and switch tournaments

```powershell
python main.py list-tournaments
python main.py select-tournament T001
```

## Player workflow

```powershell
python main.py list-tournaments
python main.py select-tournament T001
python main.py login player P001
python main.py view-pairings
python main.py standings
python main.py my-points
python main.py logout
```

## Create new admin

```powershell
python main.py login admin admin admin123
python main.py create-admin "Jane Doe" jane mypassword123
```

## Run tests

```powershell
pytest tests/ -v
```
