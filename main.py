import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from models.tournament import Tournament
from utils.persistence import save_tournament, load_tournament, DEFAULT_DATA_PATH
from utils.pairing import generate_pairings
from utils.standings import get_standings

console = Console()

_tournament: Tournament | None = None


def _try_auto_load() -> None:
    global _tournament
    if _tournament is None:
        loaded = load_tournament()
        if loaded is not None:
            _tournament = loaded


def _auto_save() -> None:
    if _tournament is not None:
        save_tournament(_tournament)


def get_active_tournament() -> Tournament:
    global _tournament
    if _tournament is None:
        console.print("[red]No active tournament. Use create-tournament or load first.[/red]")
        sys.exit(1)
    return _tournament


def cmd_create_tournament(args: argparse.Namespace) -> None:
    global _tournament
    _tournament = Tournament(name=args.name, tournament_id=args.id)
    _auto_save()
    console.print(f"[green]Tournament '{args.name}' created (ID: {args.id}).[/green]")


def cmd_add_player(args: argparse.Namespace) -> None:
    tournament = get_active_tournament()
    player = tournament.add_player(args.name, args.rating)
    _auto_save()
    console.print(
        f"[green]Added player {player.name} "
        f"(ID: {player.person_id}, Rating: {player.rating}).[/green]"
    )


def cmd_list_players(args: argparse.Namespace) -> None:
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
    tournament = get_active_tournament()
    try:
        matches = generate_pairings(tournament)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    if not matches:
        console.print("[yellow]No pairings could be generated.[/yellow]")
        return

    table = Table(title=f"Round {tournament.current_round} Pairings")
    table.add_column("Match ID", style="cyan")
    table.add_column("White")
    table.add_column("Black")

    for match in matches:
        p1 = tournament.get_player(match.player1_id)
        p2 = tournament.get_player(match.player2_id)
        table.add_row(
            match.match_id,
            f"{p1.name} ({p1.person_id})" if p1 else match.player1_id,
            f"{p2.name} ({p2.person_id})" if p2 else match.player2_id,
        )

    console.print(table)
    _auto_save()


def cmd_enter_result(args: argparse.Namespace) -> None:
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


def cmd_standings(args: argparse.Namespace) -> None:
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


def cmd_save(args: argparse.Namespace) -> None:
    tournament = get_active_tournament()
    path = Path(args.file) if args.file else DEFAULT_DATA_PATH
    save_tournament(tournament, path)
    console.print(f"[green]Tournament saved to {path}.[/green]")


def cmd_load(args: argparse.Namespace) -> None:
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Chess Tournament Manager CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

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

    standings_parser = subparsers.add_parser("standings", help="Show tournament standings")
    standings_parser.set_defaults(func=cmd_standings)

    save_parser = subparsers.add_parser("save", help="Save tournament to JSON")
    save_parser.add_argument("--file", "-f", help="Output file path")
    save_parser.set_defaults(func=cmd_save)

    load_parser = subparsers.add_parser("load", help="Load tournament from JSON")
    load_parser.add_argument("--file", "-f", help="Input file path")
    load_parser.set_defaults(func=cmd_load)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "create-tournament":
        _try_auto_load()
    args.func(args)


if __name__ == "__main__":
    main()
