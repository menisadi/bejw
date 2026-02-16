import csv
import io
import json
from enum import StrEnum

from rich.console import Console
from rich.table import Table, box

from .models import ReadingList

class OutputFormat(StrEnum):
    TABLE = "table"
    TSV = "tsv"
    CSV = "csv"
    JSONL = "jsonl"


class ColorMode(StrEnum):
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


def _link_headers(show_ids: bool) -> list[str]:
    headers = ["no"]
    if show_ids:
        headers.append("id")
    headers.extend(["status", "title", "url"])
    return headers


def _visible_links(reading_list: ReadingList, include_read: bool) -> list:
    return reading_list.ordered_links() if include_read else reading_list.unread_links()


def _link_values(
    reading_list: ReadingList, show_ids: bool, include_read: bool
) -> list[list[str]]:
    rows: list[list[str]] = []
    ordered = _visible_links(reading_list, include_read)
    for index, link in enumerate(ordered, start=1):
        row: list[str] = [str(index)]
        if show_ids:
            row.append(link.id)
        row.append("read" if link.read_at is not None else "unread")
        row.append(link.title)
        row.append(link.url)
        rows.append(row)
    return rows


def _render_delimited(
    reading_list: ReadingList,
    show_ids: bool,
    include_header: bool,
    delimiter: str,
    include_read: bool,
) -> str:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter, lineterminator="\n")

    if include_header:
        writer.writerow(_link_headers(show_ids))
    writer.writerows(_link_values(reading_list, show_ids, include_read))
    return output.getvalue()


def _render_jsonl(reading_list: ReadingList, show_ids: bool, include_read: bool) -> str:
    """Render the reading list as JSONL (JSON Lines) format."""
    lines = []
    ordered = _visible_links(reading_list, include_read)
    for index, link in enumerate(ordered, start=1):
        payload = {
            "number": index,
            "status": "read" if link.read_at is not None else "unread",
            "title": link.title,
            "url": link.url,
        }
        if show_ids:
            payload["id"] = link.id
        lines.append(json.dumps(payload, ensure_ascii=False))
    # Join the lines. Add a final newline at the end if there are any lines
    return "\n".join(lines) + ("\n" if lines else "")


def render_links(
    reading_list: ReadingList,
    show_ids: bool = False,
    output_format: OutputFormat = OutputFormat.TABLE,
    include_header: bool = True,
    include_read: bool = False,
    color: ColorMode = ColorMode.AUTO,
) -> None:
    if color == ColorMode.ALWAYS:
        render_console = Console(force_terminal=True)
    elif color == ColorMode.NEVER:
        render_console = Console(no_color=True)
    else:
        render_console = Console()

    if output_format == OutputFormat.TSV:
        render_console.file.write(
            _render_delimited(
                reading_list, show_ids, include_header, "\t", include_read
            )
        )
        return
    if output_format == OutputFormat.CSV:
        render_console.file.write(
            _render_delimited(reading_list, show_ids, include_header, ",", include_read)
        )
        return
    if output_format == OutputFormat.JSONL:
        render_console.file.write(_render_jsonl(reading_list, show_ids, include_read))
        return

    # If non of the above formats were selected, rendering a table
    table = Table(
        title="Bejeweled Reading List",
        box=box.SIMPLE,
        title_justify="left",
        title_style="bold red",
    )
    table.add_column("No.", style="cyan", no_wrap=True)
    if show_ids:
        table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Status", style="yellow", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("URL", style="green")

    ordered = _visible_links(reading_list, include_read)
    for index, link in enumerate(ordered, start=1):
        row = [str(index)]
        if show_ids:
            row.append(str(link.id))
        row.append("read" if link.read_at is not None else "unread")
        row.append(link.title)
        row.append(link.url)
        table.add_row(*row)

    render_console.print(table)
