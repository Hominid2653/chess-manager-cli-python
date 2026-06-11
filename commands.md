.\venv\Scripts\Activate.ps1

# Admin sets up tournament
python main.py login admin admin admin123
python main.py create-tournament "Spring Open" T001
python main.py add-player Alice 1500
python main.py add-player Bob 1400
python main.py pair-round
python main.py logout

# Player views their tournament
python main.py login player P001
python main.py view-pairings
python main.py standings
python main.py my-points

.\venv\Scripts\Activate.ps1

# Create new admin
# Log in as an existing admin
python main.py login admin admin admin123
python main.py create-admin "Jane Doe" jane mypassword123
python main.py create-admin "Jane Doe" jane mypassword123


login / logout / whoami / create-admin — admin & player auth
view-pairings / my-points — player read-only views