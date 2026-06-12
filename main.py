"""CLI entry point"""

import argparse
import sys
from pathlib import Path

from models.tournament import Tournament
from utils.persistence import (
    save_tournament,
    load_tournament,
    load_tournament_by_id,
    load_tournament_from_path,
    load_active_tournament,
    list_tournament_summaries,
    set_active_tournament_id,
    get_active_tournament_id,
    tournament_exists,
    DEFAULT_DATA_PATH,
)
from utils.pairing import generate_pairings
from utils.standings import get_standings
from utils.auth import (
    login_admin,
    login_player,
    clear_session,
    get_session,
    is_admin,
    is_player,
    create_admin,
    ensure_default_admin,
    get_logged_in_player_id,
    get_session_tournament_id,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
)
from utils.console_theme import (
    console,
    print_success,
    print_info,
    print_error,
    print_warning,
    make_table,
    id_column_style,
    role_badge,
    ADMIN_HEADER,
    PLAYER_HEADER,
)

_tournament: Tournament | None = None


def _try_auto_load() -> None:
    """Load the selected tournament from JSON if not already in memory."""
    global _tournament
    if _tournament is None:
        loaded = load_active_tournament()
        if loaded is not None:
            _tournament = loaded


def _auto_save() -> None:
    """Save the active tournament to JSON after changes."""
    if _tournament is not None:
        save_tournament(_tournament)


def _set_active_tournament(tournament: Tournament) -> None:
    """Set the in-memory and persisted active tournament."""
    global _tournament
    _tournament = tournament
    set_active_tournament_id(tournament.tournament_id)


def get_active_tournament() -> Tournament:
    """Return the selected tournament or exit with an error."""
    global _tournament
    if _tournament is None:
        _try_auto_load()
    if _tournament is None:
        print_error(
            "No tournament selected. Use list-tournaments, then select-tournament <id>."
        )
        sys.exit(1)
    return _tournament


def _resolve_tournament_for_player_login(tournament_id: str | None) -> tuple[Tournament, str]:
    """Pick the tournament a player is logging into."""
    if tournament_id:
        if not tournament_exists(tournament_id):
            print_error(f"Tournament '{tournament_id}' not found.")
            sys.exit(1)
        tournament = load_tournament_by_id(tournament_id)
        if tournament is None:
            print_error(f"Could not load tournament '{tournament_id}'.")
            sys.exit(1)
        _set_active_tournament(tournament)
        return tournament, tournament_id

    active_id = get_active_tournament_id()
    if active_id is None:
        print_error(
            "Select a tournament first: list-tournaments, then select-tournament <id>."
        )
        sys.exit(1)

    tournament = get_active_tournament()
    return tournament, active_id


def require_admin() -> None:
    """Block the command unless an admin is logged in."""
    if not is_admin():
        print_error("Admin login required. Use: login admin <username> <password>")
        sys.exit(1)


def require_player() -> None:
    """Block the command unless a player is logged in."""
    if not is_player():
        print_error("Player login required. Use: login player <player_id>")
        sys.exit(1)


def require_admin_or_player() -> None:
    """Block the command unless an admin or player is logged in."""
    if not is_admin() and not is_player():
        print_error("Login required. Use login admin or login player.")
        sys.exit(1)


def cmd_login(args: argparse.Namespace) -> None:
    """Log in as admin or player."""
    role = args.role.lower()

    if role == "admin":
        try:
            admin = login_admin(args.username, args.password)
        except ValueError as exc:
            print_error(str(exc))
            sys.exit(1)
        print_success(f"{admin.name} logged in successfully.", role="admin")
        return

    if role == "player":
        tournament, tournament_id = _resolve_tournament_for_player_login(args.tournament_id)
        try:
            login_player(args.player_id, tournament, tournament_id)
        except ValueError as exc:
            print_error(str(exc))
            sys.exit(1)
        player = tournament.get_player(args.player_id)
        print_success(
            f"{player.name} ({args.player_id}) logged in to {tournament.name} ({tournament_id}).",
            role="player",
        )
        return

    print_error("Role must be 'admin' or 'player'.")
    sys.exit(1)


def cmd_logout(args: argparse.Namespace) -> None:
    """Log out the current user."""
    session = get_session()
    if session is None:
        print_warning("No active session.")
        return

    role = session.get("role")
    name = session.get("name", "User")
    clear_session()
    print_success(f"{name} logged out.", role=role)


def cmd_whoami(args: argparse.Namespace) -> None:
    """Show the currently logged-in user."""
    session = get_session()
    if session is None:
        print_warning("Not logged in.")
        return

    name = session.get("name", "Unknown")
    active_id = get_active_tournament_id()
    active_label = f" | Tournament: {active_id}" if active_id else ""

    if session["role"] == "player":
        tournament_id = session.get("tournament_id", active_id or "none")
        print_info(
            f"{role_badge('player')}{name} (ID: {session.get('player_id')}) "
            f"[{tournament_id}]{active_label}",
            role="player",
        )
    else:
        print_info(
            f"{role_badge('admin')}{name} (@{session.get('username')}){active_label}",
            role="admin",
        )


def cmd_create_admin(args: argparse.Namespace) -> None:
    """Create a new admin account."""
    require_admin()
    try:
        admin = create_admin(args.name, args.username, args.password)
    except ValueError as exc:
        print_error(str(exc))
        sys.exit(1)
    print_success(
        f"Created {admin.name} (username: {admin.username}, ID: {admin.person_id}).",
        role="admin",
    )


def cmd_list_tournaments(args: argparse.Namespace) -> None:
    """List all saved tournaments."""
    require_admin_or_player()
    summaries = list_tournament_summaries()
    active_id = get_active_tournament_id()
    role = "admin" if is_admin() else "player"

    if not summaries:
        print_warning("No tournaments found. An admin can create one with create-tournament.")
        return

    table = make_table("Tournaments", role=role)
    table.add_column("ID", style=id_column_style(role))
    table.add_column("Name", style=ADMIN_HEADER if role == "admin" else PLAYER_HEADER)
    table.add_column("Players", justify="right")
    table.add_column("Round", justify="right")
    table.add_column("Selected", justify="center")

    for item in summaries:
        selected = "yes" if item["tournament_id"] == active_id else ""
        table.add_row(
            item["tournament_id"],
            item["name"],
            str(item["player_count"]),
            str(item["current_round"]),
            selected,
        )

    console.print(table)


def cmd_select_tournament(args: argparse.Namespace) -> None:
    """Select which tournament to work with."""
    require_admin_or_player()
    tournament_id = args.tournament_id

    if not tournament_exists(tournament_id):
        print_error(f"Tournament '{tournament_id}' not found. Use list-tournaments.")
        sys.exit(1)

    tournament = load_tournament_by_id(tournament_id)
    if tournament is None:
        print_error(f"Could not load tournament '{tournament_id}'.")
        sys.exit(1)

    _set_active_tournament(tournament)
    role = "admin" if is_admin() else "player"
    print_success(
        f"Selected '{tournament.name}' ({tournament_id}).",
        role=role,
    )


def cmd_create_tournament(args: argparse.Namespace) -> None:
    """Create a new tournament."""
    require_admin()
    if tournament_exists(args.id):
        print_error(f"Tournament ID '{args.id}' already exists. Choose another ID.")
        sys.exit(1)

    tournament = Tournament(name=args.name, tournament_id=args.id)
    _set_active_tournament(tournament)
    _auto_save()
    print_success(f"Tournament '{args.name}' created (ID: {args.id}).", role="admin")


def cmd_add_player(args: argparse.Namespace) -> None:
    """Add a player to the tournament."""
    require_admin()
    tournament = get_active_tournament()
    player = tournament.add_player(args.name, args.rating)
    _auto_save()
    print_success(
        f"Added {player.name} (ID: {player.person_id}, Rating: {player.rating}).",
        role="admin",
    )


def cmd_list_players(args: argparse.Namespace) -> None:
    """List all registered players."""
    require_admin()
    tournament = get_active_tournament()
    if not tournament.players:
        print_warning("No players registered yet.")
        return

    table = make_table("Registered Players", role="admin")
    table.add_column("ID", style=id_column_style("admin"))
    table.add_column("Name", style=ADMIN_HEADER)
    table.add_column("Rating", justify="right")
    table.add_column("Points", justify="right")

    for player in tournament.players:
        table.add_row(player.person_id, player.name, str(player.rating), f"{player.points:.1f}")

    console.print(table)


def cmd_pair_round(args: argparse.Namespace) -> None:
    """Generate pairings for the next round."""
    require_admin()
    tournament = get_active_tournament()
    try:
        matches = generate_pairings(tournament)
    except ValueError as exc:
        print_error(str(exc))
        sys.exit(1)

    if not matches:
        print_warning("No pairings could be generated.")
        return

    _print_pairings_table(tournament, tournament.current_round, role="admin")
    _auto_save()


def cmd_enter_result(args: argparse.Namespace) -> None:
    """Record a match result and update player points."""
    require_admin()
    tournament = get_active_tournament()
    match = next((m for m in tournament.matches if m.match_id == args.match_id), None)
    if match is None:
        print_error(f"Match '{args.match_id}' not found.")
        sys.exit(1)
    if match.is_complete:
        print_error(f"Match '{args.match_id}' already has a result.")
        sys.exit(1)

    result = args.result.lower()
    if result not in ("win", "loss", "draw"):
        print_error("Result must be win, loss, or draw.")
        sys.exit(1)

    white = tournament.get_player(match.player1_id)
    black = tournament.get_player(match.player2_id)
    if white is None or black is None:
        print_error("One or both players not found for this match.")
        sys.exit(1)

    if result == "win":
        white.add_result("win")
        black.add_result("loss")
    elif result == "loss":
        white.add_result("loss")
        black.add_result("win")
    else:
        white.add_result("draw")
        black.add_result("draw")

    match.result = result
    _auto_save()
    print_success(
        f"Result recorded for {match.match_id}: "
        f"{white.name} vs {black.name} -> {result} (white's perspective).",
        role="admin",
    )


def cmd_save(args: argparse.Namespace) -> None:
    """Save the tournament to a JSON file."""
    require_admin()
    tournament = get_active_tournament()
    path = Path(args.file) if args.file else None
    save_tournament(tournament, path)
    saved_to = path or f"data/tournaments/{tournament.tournament_id}.json"
    print_success(f"Tournament saved to {saved_to}.", role="admin")


def cmd_load(args: argparse.Namespace) -> None:
    """Load a tournament from a JSON file and select it."""
    require_admin()
    path = Path(args.file) if args.file else DEFAULT_DATA_PATH
    try:
        loaded = load_tournament_from_path(path)
    except ValueError as exc:
        print_error(str(exc))
        sys.exit(1)

    if loaded is None:
        print_error(f"No tournament file found at {path}.")
        sys.exit(1)

    save_tournament(loaded)
    _set_active_tournament(loaded)
    print_success(
        f"Tournament '{loaded.name}' ({loaded.tournament_id}) loaded and selected.",
        role="admin",
    )


def _print_pairings_table(tournament: Tournament, round_num: int, role: str | None = None) -> None:
    """Display pairings for a round in a role-colored table."""
    matches = tournament.get_round_matches(round_num)
    if not matches:
        print_warning(f"No pairings for round {round_num}.")
        return

    resolved_role = role or ("admin" if is_admin() else "player" if is_player() else None)
    header = ADMIN_HEADER if resolved_role == "admin" else PLAYER_HEADER

    table = make_table(f"Round {round_num} Pairings", role=resolved_role)
    table.add_column("Match ID", style=id_column_style(resolved_role))
    table.add_column("White", style=header)
    table.add_column("Black", style=header)
    table.add_column("Result")

    for match in matches:
        p1 = tournament.get_player(match.player1_id)
        p2 = tournament.get_player(match.player2_id)
        table.add_row(
            match.match_id,
            f"{p1.name} ({p1.person_id})" if p1 else match.player1_id,
            f"{p2.name} ({p2.person_id})" if p2 else match.player2_id,
            match.result or "pending",
        )

    console.print(table)


def cmd_view_pairings(args: argparse.Namespace) -> None:
    """View pairings for a round."""
    require_admin_or_player()
    tournament = get_active_tournament()
    round_num = args.round if args.round else tournament.current_round

    if round_num < 1:
        print_warning("No rounds have been paired yet.")
        return

    _print_pairings_table(tournament, round_num)


def cmd_standings(args: argparse.Namespace) -> None:
    """Show the tournament leaderboard."""
    require_admin_or_player()
    tournament = get_active_tournament()
    standings = get_standings(tournament)

    role = "admin" if is_admin() else "player"
    header = ADMIN_HEADER if role == "admin" else PLAYER_HEADER

    table = make_table(f"Standings — {tournament.name}", role=role)
    table.add_column("Rank", justify="right", style="bold")
    table.add_column("ID", style=id_column_style(role))
    table.add_column("Name", style=header)
    table.add_column("Rating", justify="right")
    table.add_column("Points", justify="right")

    player_id = get_logged_in_player_id()
    for rank, player in enumerate(standings, start=1):
        name = player.name
        if role == "player" and player.person_id == player_id:
            name = f"[{PLAYER_HEADER}]{player.name} (you)[/{PLAYER_HEADER}]"
        table.add_row(
            str(rank),
            player.person_id,
            name,
            str(player.rating),
            f"{player.points:.1f}",
        )

    console.print(table)


def cmd_my_points(args: argparse.Namespace) -> None:
    """Show the logged-in player's points and rank."""
    require_player()
    tournament = get_active_tournament()
    player_id = get_logged_in_player_id()
    session_tournament_id = get_session_tournament_id()

    if session_tournament_id and tournament.tournament_id != session_tournament_id:
        print_error(
            f"You are logged in for '{session_tournament_id}'. "
            f"Run select-tournament {session_tournament_id} first."
        )
        sys.exit(1)

    player = tournament.get_player(player_id)

    if player is None:
        print_error("Your player record was not found in this tournament.")
        sys.exit(1)

    standings = get_standings(tournament)
    rank = next(
        (i for i, p in enumerate(standings, start=1) if p.person_id == player_id),
        None,
    )

    console.print(f"[{PLAYER_HEADER}]Player:[/{PLAYER_HEADER}] {player.name} ({player.person_id})")
    console.print(f"[{PLAYER_HEADER}]Rating:[/{PLAYER_HEADER}] {player.rating}")
    console.print(f"[{PLAYER_HEADER}]Points:[/{PLAYER_HEADER}] {player.points:.1f}")
    if rank is not None:
        console.print(f"[{PLAYER_HEADER}]Rank:[/{PLAYER_HEADER}] {rank} of {len(standings)}")


def build_parser() -> argparse.ArgumentParser:
    """Set up all CLI commands and their arguments."""
    parser = argparse.ArgumentParser(
        description="Chess Tournament Manager CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    login_parser = subparsers.add_parser("login", help="Log in as admin or player")
    login_parser.add_argument("role", choices=["admin", "player"], help="Login role")
    login_parser.add_argument("username", nargs="?", help="Admin username (admin login)")
    login_parser.add_argument("password", nargs="?", help="Admin password (admin login)")
    login_parser.add_argument("--player-id", "-p", dest="player_id", help="Player ID (player login)")
    login_parser.add_argument(
        "--tournament", "-t", dest="tournament_id", help="Tournament ID (player login)"
    )
    login_parser.set_defaults(func=cmd_login)

    list_tournaments_parser = subparsers.add_parser(
        "list-tournaments", help="List all saved tournaments"
    )
    list_tournaments_parser.set_defaults(func=cmd_list_tournaments)

    select_tournament_parser = subparsers.add_parser(
        "select-tournament", help="Select a tournament to work with"
    )
    select_tournament_parser.add_argument("tournament_id", help="Tournament ID")
    select_tournament_parser.set_defaults(func=cmd_select_tournament)

    logout_parser = subparsers.add_parser("logout", help="Log out of the current session")
    logout_parser.set_defaults(func=cmd_logout)

    whoami_parser = subparsers.add_parser("whoami", help="Show the current logged-in user")
    whoami_parser.set_defaults(func=cmd_whoami)

    create_admin_parser = subparsers.add_parser("create-admin", help="Create a new admin account")
    create_admin_parser.add_argument("name", help="Admin display name")
    create_admin_parser.add_argument("username", help="Login username")
    create_admin_parser.add_argument("password", help="Login password")
    create_admin_parser.set_defaults(func=cmd_create_admin)

    create_parser = subparsers.add_parser("create-tournament", help="Create a new tournament")
    create_parser.add_argument("name", help="Tournament name")
    create_parser.add_argument("id", help="Tournament ID")
    create_parser.set_defaults(func=cmd_create_tournament)

    add_parser = subparsers.add_parser("add-player", help="Add a player to the tournament")
    add_parser.add_argument("name", help="Player name")
    add_parser.add_argument("rating", type=int, help="Player rating")
    add_parser.set_defaults(func=cmd_add_player)

    list_parser = subparsers.add_parser("list-players", help="List all registered players")
    list_parser.set_defaults(func=cmd_list_players)

    pair_parser = subparsers.add_parser("pair-round", help="Generate pairings for the next round")
    pair_parser.set_defaults(func=cmd_pair_round)

    result_parser = subparsers.add_parser("enter-result", help="Record a match result")
    result_parser.add_argument("match_id", help="Match ID")
    result_parser.add_argument(
        "result",
        help="Result from white's perspective: win, loss, or draw",
    )
    result_parser.set_defaults(func=cmd_enter_result)

    save_parser = subparsers.add_parser("save", help="Save tournament to JSON")
    save_parser.add_argument("--file", "-f", help="Output file path")
    save_parser.set_defaults(func=cmd_save)

    load_parser = subparsers.add_parser("load", help="Load tournament from JSON")
    load_parser.add_argument("--file", "-f", help="Input file path")
    load_parser.set_defaults(func=cmd_load)

    pairings_parser = subparsers.add_parser("view-pairings", help="View round pairings")
    pairings_parser.add_argument("--round", "-r", type=int, help="Round number (default: current)")
    pairings_parser.set_defaults(func=cmd_view_pairings)

    standings_parser = subparsers.add_parser("standings", help="Show tournament standings")
    standings_parser.set_defaults(func=cmd_standings)

    points_parser = subparsers.add_parser("my-points", help="View your points and rank")
    points_parser.set_defaults(func=cmd_my_points)

    return parser


def main() -> None:
    """Parse command-line args and run the selected command."""
    ensure_default_admin()

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "login" and args.role == "player":
        if not args.player_id:
            if args.username and not args.password:
                args.player_id = args.username
            else:
                print_error("Player login requires a player ID: login player P001")
                sys.exit(1)

    if args.command == "login" and args.role == "admin":
        if not args.username or not args.password:
            print_error("Admin login requires username and password.")
            print_info(
                f"Default: {DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}",
                role="admin",
            )
            sys.exit(1)

    if args.command not in ("create-tournament", "list-tournaments"):
        _try_auto_load()

    args.func(args)


if __name__ == "__main__":
    main()
