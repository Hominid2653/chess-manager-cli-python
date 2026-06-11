.\venv\Scripts\Activate.ps1

python main.py create-tournament "Spring Open" T001
python main.py add-player Alice 1500
python main.py add-player Bob 1400
python main.py list-players
python main.py pair-round
python main.py enter-result M001 win
python main.py standings
python main.py save    # optional with autosave
python main.py load    # load from a custom file with --file