from rich.console import Console
from rich.table import Table

from models import ReadingList

console = Console()


def render_links(reading_list: ReadingList) -> None:
    table = Table(title="Bejeweled Reading List")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("URL", style="green")

    for link in reading_list.links:
        table.add_row(str(link.id), link.title, link.url)

    console.print(table)
