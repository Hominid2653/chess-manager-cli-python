"""Role-based colors for rich console output."""

from rich.console import Console
from rich.table import Table

from utils.auth import is_admin, is_player

console = Console()

# Admin theme: green
ADMIN_STYLE = "green"
ADMIN_HEADER = "bold green"
ADMIN_ACCENT = "bright_green"

# Player theme: white
PLAYER_STYLE = "white"
PLAYER_HEADER = "bold white"
PLAYER_ACCENT = "white"


def _resolve_role(role: str | None = None) -> str | None:
    """Return 'admin', 'player', or None based on input"""
    if role in ("admin", "player"):
        return role
    if is_admin():
        return "admin"
    elif is_player():
        return "player"
    return None


def role_badge(role: str | None = None) -> str:
    """Return a colored role label for message prefixes."""
    resolved = _resolve_role(role)
    if resolved == "admin":
        return f"[{ADMIN_HEADER}] ADMIN [/]"
    elif resolved == "player":
        return f"[{PLAYER_HEADER}] PLAYER [/]"
    return ""


def print_success(message: str, role: str | None = None) -> None:
    """Print a success message using the role's color."""
    resolved = _resolve_role(role)
    if resolved == "admin":
        console.print(f"[{ADMIN_HEADER}]{role_badge('admin')}{message}[/{ADMIN_HEADER}]")
    elif resolved == "player":
        console.print(f"[{PLAYER_HEADER}]{role_badge('player')}{message}[/{PLAYER_HEADER}]")
    else:
        console.print(f"[green]{message}[/green]")


def print_info(message: str, role: str | None = None) -> None:
    """Print an informational message using the role's accent color."""
    resolved = _resolve_role(role)
    if resolved == "admin":
        console.print(f"[{ADMIN_ACCENT}]{message}[/{ADMIN_ACCENT}]")
    elif resolved == "player":
        console.print(f"[{PLAYER_ACCENT}]{message}[/{PLAYER_ACCENT}]")
    else:
        console.print(message)


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] [red]{message}[/red]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]{message}[/yellow]")


def make_table(title: str, role: str | None = None) -> Table:
    """Create a table styled for the current or given role."""
    resolved = _resolve_role(role)
    if resolved == "admin":
        border = ADMIN_STYLE
        title_style = ADMIN_HEADER
    elif resolved == "player":
        border = PLAYER_STYLE
        title_style = PLAYER_HEADER
    else:
        border = "white"
        title_style = "bold"

    return Table(title=f"[{title_style}]{title}[/{title_style}]", border_style=border)


def id_column_style(role: str | None = None) -> str:
    """Return the accent color for ID columns in tables."""
    resolved = _resolve_role(role)
    if resolved == "admin":
        return ADMIN_ACCENT
    elif resolved == "player":
        return PLAYER_ACCENT
    return "white"
