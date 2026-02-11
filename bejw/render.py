from rich.console import Console
from rich.table import Table, box

from .models import ReadingList

console = Console()


def render_links(reading_list: ReadingList, show_ids: bool = False) -> None:
    table = Table(
        title="Bejeweled Reading List",
        box=box.SIMPLE,
        title_justify="left",
        title_style="bold red",
    )
    if show_ids:
        table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("URL", style="green")

    for link in reading_list.links:
        row = []
        if show_ids:
            row.append(str(link.id))
        row.append(link.title)
        row.append(link.url)
        table.add_row(*row)

    console.print(table)
