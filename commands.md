# Quick command reference

Use `chess` instead of `python main.py`. See [Readme.md](Readme.md) for full setup.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Admin workflow

```powershell
chess login admin admin admin123
chess create-tournament "Spring Open" T001
chess add-player Alice 1500
chess add-player Bob 1400
chess pair-round
chess enter-result M001 win
chess standings
chess logout
```

## List and switch tournaments

```powershell
chess list-tournaments
chess select-tournament T001
```

## Player workflow

```powershell
chess list-tournaments
chess select-tournament T001
chess login player P001
chess view-pairings
chess standings
chess my-points
chess logout
```

## Create new admin

```powershell
chess login admin admin admin123
chess create-admin "Jane Doe" jane mypassword123
```

## Run tests

```powershell
pytest tests/ -v
```

## Without install (use launcher)

```powershell
.\chess login admin admin admin123
```
