"""
bejw:  A capped reading list for links that shimmer 
The reading list should be stored on  a json file under ~/.bejw/links.json
The commands are: add, remove, list, capacity and clear
add: add a link to the reading list
remove: remove a link from the reading list by id
list: display the reading list
capacity: change the capacity of the reading list
clear: clear the reading list
"""
from rich.console import Console
from rich.table import Table
import typer

DEFAULT_CAPACITY = 10
DEFAULT_FILE_PATH = "~/.bejw/links.json"

app = typer.Typer()
console = Console()

class Link:
    def __init__(self, url: str, title: str):
        self.id = id(self)
        self.url = url
        self.title = title

class ReadingList:
    def __init__(self, capacity: int = 10):
        self.capacity: int = capacity
        self.links: list[Link] = []

    def add_link(self, url: str, title: str):
        if len(self.links) >= self.capacity:
            # tell the user that the list is full and they need to remove a link before adding a new one
            console.print("[red]Reading list is full! Please remove a link before adding a new one.[/red]")

        self.links.append(Link(url, title))

    def remove_link(self, link_id: int):
        self.links = [link for link in self.links if link.id != link_id]

    def display_links(self):
        table = Table(title="Bejeweled Reading List")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("URL", style="green")

        for link in self.links:
            table.add_row(str(link.id), link.title, link.url)

        console.print(table)

    def read_from_file(self, file_path: str):
        # read the links from the json file and populate the reading list
        pass

    def write_to_file(self, file_path: str):
        # write the links to the json file
        pass

    def clear_links(self):
        self.links = []

####### Wrappers for the command line interface #######

@app.command()
def init(capacity: int = DEFAULT_CAPACITY, file_path: str = DEFAULT_FILE_PATH):
    reading_list = ReadingList(capacity)
    reading_list.write_to_file(file_path)



if __name__ == "__main__":
    app()
