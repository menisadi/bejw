"""
bejw:  A capped reading list for links that shimmer
"""

import webbrowser
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import typer
from rich import print

from .models import CapacityError, Link, ReadingList
from .render import ColorMode, OutputFormat, render_links
from .storage import load, save

DEFAULT_CAPACITY = 10
DEFAULT_FILE_PATH = "~/.bejw/links.json"

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if not value:
        return
    try:
        typer.echo(version("bejw"))
    except PackageNotFoundError:
        typer.echo("unknown")
    raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    context: typer.Context,
    show_version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the installed version and exit.",
    ),
) -> None:
    if context.invoked_subcommand is not None:
        return
    print(
        "[bold magenta]bejw[/bold magenta]: A capped reading list for links that shimmer"
    )
    print("Run with [bold cyan]--help[/bold cyan] to see commands and options.")


@app.command()
def init(
    capacity: int = DEFAULT_CAPACITY,
    file_path: str = DEFAULT_FILE_PATH,
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite an existing reading list without confirming.",
    ),
) -> None:
    """Initialize the reading list with a specified capacity and file path."""
    expanded_path = Path(file_path).expanduser()
    if expanded_path.exists() and not force:
        existing = load(file_path)
        total = len(existing.links)
        unread = len(existing.unread_links())
        typer.echo(
            f"{expanded_path} already holds {total} link{'' if total == 1 else 's'} "
            f"({unread} unread) with capacity {existing.capacity}.",
            err=True,
        )
        if not typer.confirm("Discard them and start over?"):
            typer.echo("Cancelled.")
            raise typer.Exit(code=1)
    reading_list = ReadingList(capacity=capacity)
    save(reading_list, file_path)
    typer.echo(f"Initialized reading list at {expanded_path} with capacity {capacity}")


def _prompt_replace(reading_list: ReadingList, url: str, title: str) -> Link | None:
    """Show unread links and let the user pick one to replace, or cancel."""
    from rich.console import Console
    from rich.table import Table, box

    console = Console(stderr=True)
    unread = reading_list.unread_links()

    console.print(
        "[bold yellow]Reading list is full![/bold yellow] Pick a link to replace:\n"
    )

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("no", style="cyan", justify="right", no_wrap=True)
    table.add_column("title", style="magenta")
    for index, link in enumerate(unread, start=1):
        table.add_row(str(index), link.title)
    console.print(table)

    choice = typer.prompt(
        "Replace #  (Enter to cancel)", default="", show_default=False
    )
    if choice == "":
        typer.echo("Cancelled.")
        return None
    try:
        number = int(choice)
    except ValueError:
        typer.echo("Invalid number. Cancelled.")
        return None
    new_link = reading_list.replace_by_number(number, url, title)
    if new_link is None:
        typer.echo("No link found with that number. Cancelled.")
        return None
    return new_link


@app.command()
def add(url: str, title: str, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Add a link to the reading list."""
    reading_list = load(file_path)
    try:
        link = reading_list.add_link(url, title)
    except CapacityError:
        link = _prompt_replace(reading_list, url, title)
        if link is None:
            raise typer.Exit(code=1)
    save(reading_list, file_path)
    ordered = reading_list.unread_links()
    number = next(
        (index for index, item in enumerate(ordered, start=1) if item.id == link.id),
        len(ordered),
    )
    typer.echo(f"Added #{number}")


@app.command()
def remove(number: int, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Remove a link from the reading list by number."""
    reading_list = load(file_path)
    removed = reading_list.remove_by_number(number)
    save(reading_list, file_path)
    if not removed:
        typer.echo("No link found with that number.")
        raise typer.Exit(code=1)


@app.command()
def read(number: int, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Open a link from the reading list by number."""
    reading_list = load(file_path)
    unread = reading_list.unread_links()
    if number < 1 or number > len(unread):
        typer.echo("No link found with that number.")
        raise typer.Exit(code=1)

    url = unread[number - 1].url
    webbrowser.open(url)
    typer.echo(f"Opened #{number}: {url}")


@app.command("mark-read")
def mark_read(number: int, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Mark a link as read by number."""
    reading_list = load(file_path)
    marked = reading_list.mark_read_by_number(number)
    if not marked:
        typer.echo("No link found with that number.")
        raise typer.Exit(code=1)
    save(reading_list, file_path)
    typer.echo(f"Marked #{number} as read: {marked.title}")


@app.command()
def list(
    file_path: str = DEFAULT_FILE_PATH,
    show_ids: bool = False,
    include_read: bool = typer.Option(
        False,
        "--include-read",
        help="Include links that have been marked as read.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--format",
        "-f",
        help="Output format: table, tsv, csv, or jsonl.",
    ),
    color: ColorMode = typer.Option(
        ColorMode.AUTO,
        "--color",
        help="Color mode for output: auto, always, or never.",
    ),
    no_header: bool = typer.Option(
        False,
        "--no-header",
        help="Omit the header row for tsv and csv output.",
    ),
) -> None:
    """Display the reading list."""
    reading_list = load(file_path)
    render_links(
        reading_list,
        show_ids=show_ids,
        output_format=output_format,
        include_header=not no_header,
        include_read=include_read,
        color=color,
    )


def _humanize_age(timestamp: str) -> str:
    """Render an ISO timestamp as a rough age like '3 days ago'."""
    try:
        changed_at = datetime.fromisoformat(timestamp)
    except ValueError:
        return "at an unknown time"
    if changed_at.tzinfo is None:
        changed_at = changed_at.replace(tzinfo=UTC)
    seconds = (datetime.now(UTC) - changed_at).total_seconds()
    if seconds < 60:
        return "just now"
    minutes = seconds / 60
    if minutes < 60:
        return _ago(int(minutes), "minute")
    hours = minutes / 60
    if hours < 24:
        return _ago(int(hours), "hour")
    return _ago(int(hours / 24), "day")


def _ago(count: int, unit: str) -> str:
    return f"{count} {unit} ago" if count == 1 else f"{count} {unit}s ago"


def _capacity_trace(reading_list: ReadingList) -> str | None:
    """Describe the last capacity change, or None if it was never changed."""
    changed_at = reading_list.capacity_changed_at
    previous = reading_list.previous_capacity
    if changed_at is None or previous is None:
        return None
    direction = "raised" if reading_list.capacity > previous else "lowered"
    return f"({direction} from {previous}, {_humanize_age(changed_at)})"


@app.command()
def capacity(
    value: int = typer.Argument(None),
    file_path: str = DEFAULT_FILE_PATH,
) -> None:
    """Show or change the capacity of the reading list."""
    reading_list = load(file_path)
    if value is None:
        typer.echo(reading_list.capacity)
        trace = _capacity_trace(reading_list)
        if trace is not None:
            typer.echo(trace, err=True)
        return
    try:
        reading_list.set_capacity(value)
    except (CapacityError, ValueError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)
    save(reading_list, file_path)
    typer.echo(f"Capacity set to {value}")


@app.command()
def clear(file_path: str = DEFAULT_FILE_PATH) -> None:
    """Clear the reading list."""
    reading_list = load(file_path)
    reading_list.clear_links()
    save(reading_list, file_path)
    typer.echo("Reading list cleared")


if __name__ == "__main__":
    app()
