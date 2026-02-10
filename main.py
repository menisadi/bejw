from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, ListView, Label
from textual.binding import Binding

class Bejeweled(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "focus_input", "Add Link"),
        Binding("d", "delete_link", "Delete"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Paste a link to make it shimmer...", id="link_input")
        yield ListView(id="link_list")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def action_focus_input(self) -> None:
        self.query_one(Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        url = event.value.strip()
        if url:
            # Here is where your Hard Cap logic will go!
            self.query_one(ListView).append(ListItem(Label(url)))
            self.query_one(Input).value = ""

if __name__ == "__main__":
    Bejeweled().run()
