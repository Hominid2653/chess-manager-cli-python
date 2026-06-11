"""CLI entry point for the chess tournament manager."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from models.tournament import Tournament
from utils.persistence import save_tournament, load_tournament, DEFAULT_DATA_PATH
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
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
)

console = Console()
_tournament: Tournament | None = None


def _try_auto_load() -> None:
    """Load tournament from JSON if not already in memory."""
    global _tournament
    if _tournament is None:
        loaded = load_tournament()
        if loaded is not None:
            _tournament = loaded


def _auto_save() -> None:
    """Save tournament to JSON after changes."""
    if _tournament is not None:
        save_tournament(_tournament)


def get_active_tournament() -> Tournament:
    """Return the active tournament or exit with an error."""
    global _tournament
    if _tournament is None:
        console.print("[red]No active tournament. Use create-tournament or load first.[/red]")
        sys.exit(1)
    return _tournament


def require_admin() -> None:
    """Block the command unless an admin is logged in."""
    if not is_admin():
        console.print("[red]Admin login required. Use: login admin <username> <password>[/red]")
        sys.exit(1)


def require_player() -> None:
    """Block the command unless a player is logged in."""
    if not is_player():
        console.print("[red]Player login required. Use: login player <player_id>[/red]")
        sys.exit(1)


def require_admin_or_player() -> None:
    """Block the command unless an admin or player is logged in."""
    if not is_admin() and not is_player():
        console.print("[red]Login required. Use login admin or login player.[/red]")
        sys.exit(1)


def cmd_login(args: argparse.Namespace) -> None:
    """Log in as admin or player."""
    role = args.role.lower()

    if role == "admin":
        try:
            admin = login_admin(args.username, args.password)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            sys.exit(1)
        console.print(f"[green]Admin '{admin.name}' logged in successfully.[/green]")
        return

    if role == "player":
        tournament = get_active_tournament()
        try:
            login_player(args.player_id, tournament)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            sys.exit(1)
        player = tournament.get_player(args.player_id)
        console.print(f"[green]Player '{player.name}' ({args.player_id}) logged in.[/green]")
        return

    console.print("[red]Role must be 'admin' or 'player'.[/red]")
    sys.exit(1)


def cmd_logout(args: argparse.Namespace) -> None:
    """Log out the current user."""
    session = get_session()
    if session is None:
        console.print("[yellow]No active session.[/yellow]")
        return
    name = session.get("name", "User")
    clear_session()
    console.print(f"[green]{name} logged out.[/green]")


def cmd_whoami(args: argparse.Namespace) -> None:
    """Show the currently logged-in user."""
    session = get_session()
    if session is None:
        console.print("[yellow]Not logged in.[/yellow]")
        return

    role = session["role"].capitalize()
    name = session.get("name", "Unknown")
    if session["role"] == "player":
        console.print(f"[cyan]{role}:[/cyan] {name} (ID: {session.get('player_id')})")
    else:
        console.print(f"[cyan]{role}:[/cyan] {name} (@{session.get('username')})")


def cmd_create_admin(args: argparse.Namespace) -> None:
    """Create a new admin account."""
    require_admin()
    try:
        admin = create_admin(args.name, args.username, args.password)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)
    console.print(
        f"[green]Admin '{admin.name}' created "
        f"(username: {admin.username}, ID: {admin.person_id}).[/green]"
    )


def cmd_create_tournament(args: argparse.Namespace) -> None:
    """Create a new tournament."""
    require_admin()
    global _tournament
    _tournament = Tournament(name=args.name, tournament_id=args.id)
    _auto_save()
    console.print(f"[green]Tournament '{args.name}' created (ID: {args.id}).[/green]")


def cmd_add_player(args: argparse.Namespace) -> None:
    """Add a player to the tournament."""
    require_admin()
    tournament = get_active_tournament()
    player = tournament.add_player(args.name, args.rating)
    _auto_save()
    console.print(
        f"[green]Added player {player.name} "
        f"(ID: {player.person_id}, Rating: {player.rating}).[/green]"
    )


def cmd_list_players(args: argparse.Namespace) -> None:
    """List all registered players."""
    require_admin()
    tournament = get_active_tournament()
    if not tournament.players:
        console.print("[yellow]No players registered yet.[/yellow]")
        return

    table = Table(title="Registered Players")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
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
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    if not matches:
        console.print("[yellow]No pairings could be generated.[/yellow]")
        return

    _print_pairings_table(tournament, tournament.current_round)
    _auto_save()


def cmd_enter_result(args: argparse.Namespace) -> None:
    """Record a match result and update player points."""
    require_admin()
    tournament = get_active_tournament()
    match = next((m for m in tournament.matches if m.match_id == args.match_id), None)
    if match is None:
        console.print(f"[red]Match '{args.match_id}' not found.[/red]")
        sys.exit(1)
    if match.is_complete:
        console.print(f"[red]Match '{args.match_id}' already has a result.[/red]")
        sys.exit(1)

    result = args.result.lower()
    if result not in ("win", "loss", "draw"):
        console.print("[red]Result must be win, loss, or draw.[/red]")
        sys.exit(1)

    white = tournament.get_player(match.player1_id)
    black = tournament.get_player(match.player2_id)
    if white is None or black is None:
        console.print("[red]One or both players not found for this match.[/red]")
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
    console.print(
        f"[green]Result recorded for {match.match_id}: "
        f"{white.name} vs {black.name} -> {result} (white's perspective).[/green]"
    )


def cmd_save(args: argparse.Namespace) -> None:
    """Save the tournament to a JSON file."""
    require_admin()
    tournament = get_active_tournament()
    path = Path(args.file) if args.file else DEFAULT_DATA_PATH
    save_tournament(tournament, path)
    console.print(f"[green]Tournament saved to {path}.[/green]")


def cmd_load(args: argparse.Namespace) -> None:
    """Load a tournament from a JSON file."""
    require_admin()
    global _tournament
    path = Path(args.file) if args.file else DEFAULT_DATA_PATH
    try:
        loaded = load_tournament(path)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    if loaded is None:
        console.print(f"[red]No tournament file found at {path}.[/red]")
        sys.exit(1)

    _tournament = loaded
    console.print(f"[green]Tournament '{loaded.name}' loaded from {path}.[/green]")


def _print_pairings_table(tournament: Tournament, round_num: int) -> None:
    """Display pairings for a round in a table."""
    matches = tournament.get_round_matches(round_num)
    if not matches:
        console.print(f"[yellow]No pairings for round {round_num}.[/yellow]")
        return

    table = Table(title=f"Round {round_num} Pairings")
    table.add_column("Match ID", style="cyan")
    table.add_column("White")
    table.add_column("Black")
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
        console.print("[yellow]No rounds have been paired yet.[/yellow]")
        return

    _print_pairings_table(tournament, round_num)


def cmd_standings(args: argparse.Namespace) -> None:
    """Show the tournament leaderboard."""
    require_admin_or_player()
    tournament = get_active_tournament()
    standings = get_standings(tournament)

    table = Table(title=f"Standings — {tournament.name}")
    table.add_column("Rank", justify="right", style="bold")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Rating", justify="right")
    table.add_column("Points", justify="right")

    for rank, player in enumerate(standings, start=1):
        table.add_row(
            str(rank),
            player.person_id,
            player.name,
            str(player.rating),
            f"{player.points:.1f}",
        )

    console.print(table)


def cmd_my_points(args: argparse.Namespace) -> None:
    """Show the logged-in player's points and rank."""
    require_player()
    tournament = get_active_tournament()
    player_id = get_logged_in_player_id()
    player = tournament.get_player(player_id)

    if player is None:
        console.print("[red]Your player record was not found in this tournament.[/red]")
        sys.exit(1)

    standings = get_standings(tournament)
    rank = next(
        (i for i, p in enumerate(standings, start=1) if p.person_id == player_id),
        None,
    )

    console.print(f"[bold]Player:[/bold] {player.name} ({player.person_id})")
    console.print(f"[bold]Rating:[/bold] {player.rating}")
    console.print(f"[bold]Points:[/bold] {player.points:.1f}")
    if rank is not None:
        console.print(f"[bold]Rank:[/bold] {rank} of {len(standings)}")


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
    login_parser.set_defaults(func=cmd_login)

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
                console.print("[red]Player login requires a player ID: login player P001[/red]")
                sys.exit(1)

    if args.command == "login" and args.role == "admin":
        if not args.username or not args.password:
            console.print(
                f"[red]Admin login requires username and password.[/red]\n"
                f"[dim]Default: {DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}[/dim]"
            )
            sys.exit(1)

    if args.command != "create-tournament":
        _try_auto_load()

    args.func(args)


if __name__ == "__main__":
    main()
