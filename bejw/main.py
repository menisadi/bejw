"""
bejw:  A capped reading list for links that shimmer
"""
from pathlib import Path

import typer

from .models import CapacityError, ReadingList
from .render import render_links
from .storage import load, save

DEFAULT_CAPACITY = 10
DEFAULT_FILE_PATH = "~/.bejw/links.json"

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(context: typer.Context) -> None:
    """Entry point that shows basic info when no subcommand is provided."""
    if context.invoked_subcommand is not None:
        return
    typer.echo("bejw: A capped reading list for links that shimmer")
    typer.echo("Run with --help to see commands and options.")


@app.command()
def init(capacity: int = DEFAULT_CAPACITY, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Initialize the reading list with a specified capacity and file path."""
    # NOTE: this will override existing reading list
    # TODO: add a confirmation prompt before overriding
    reading_list = ReadingList(capacity=capacity)
    save(reading_list, file_path)
    expanded_path = str(Path(file_path).expanduser())
    typer.echo(f"Initialized reading list at {expanded_path} with capacity {capacity}")


@app.command()
def add(url: str, title: str, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Add a link to the reading list."""
    reading_list = load(file_path)
    try:
        link = reading_list.add_link(url, title)
    except CapacityError:
        typer.echo("Reading list is full! Please remove a link before adding a new one.")
        raise typer.Exit(code=1)
    save(reading_list, file_path)
    typer.echo(f"Added {link.id}")


@app.command()
def remove(link_id: str, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Remove a link from the reading list by id."""
    reading_list = load(file_path)
    removed = reading_list.remove_link(link_id)
    save(reading_list, file_path)
    if not removed:
        typer.echo("No link found with that id.")
        raise typer.Exit(code=1)


@app.command()
def list(file_path: str = DEFAULT_FILE_PATH, show_ids: bool = False) -> None:
    """Display the reading list."""
    reading_list = load(file_path)
    render_links(reading_list, show_ids=show_ids)


@app.command()
def capacity(value: int, file_path: str = DEFAULT_FILE_PATH) -> None:
    """Change the capacity of the reading list."""
    reading_list = load(file_path)
    reading_list.capacity = value
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
