# Chess Tournament Manager CLI - Project Plan

## Overview
A Python CLI application for managing chess tournaments. The system allows an admin to register players, create pairings, record results, and generate standings, while players can view their rankings and match information.

---

## Core Features

### 1. Tournament Management
- Create a new tournament
- Store tournament data in JSON
- Load existing tournament

### 2. Player Management
- Add players with name and rating
- View all registered players
- Assign unique player IDs

### 3. Pairing System
- Generate pairings for Round 1 based on rating
- Generate subsequent pairings based on points
- Prevent duplicate matchups where possible

### 4. Match Results
- Record match results (win, loss, draw)
- Automatically update player points

### 5. Standings System
- Sort players by points
- Break ties using rating
- Display leaderboard in CLI

---

## OOP Design

### Classes
- Person (base class)
- Admin (inherits Person)
- Player (inherits Person)
- Tournament
- Match

### Relationships
- Tournament contains Players
- Tournament contains Matches
- Matches link two Players

---

## CLI Design (argparse)

### Commands
- create-tournament
- add-player
- list-players
- pair-round
- enter-result
- standings
- save
- load

---

## Data Persistence

- JSON-based storage in /data folder
- Safe load/save using try-except
- Auto-create file if missing

---

## External Libraries

- rich (for better CLI tables)
- pytest (for testing)

---

## Testing Strategy

- Test Player point updates
- Test pairing logic
- Test standings sorting
- Mock JSON file operations

---

## File Structure

chess-manager/
├── main.py
├── models/
├── utils/
├── data/
├── tests/
├── requirements.txt
└── README.md

---

## MVP Goals

- Player registration
- Pairing system
- Result entry
- Standings generation
- JSON persistence
