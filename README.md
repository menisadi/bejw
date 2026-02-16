# bejw

A small CLI to keep a capped reading list of links in a local JSON file.

## Install

```bash
uv sync
```

## Usage

```bash
python main.py --help
python main.py init --capacity 10
python main.py add "https://example.com" "Example"
python main.py list
python main.py list --include-read
python main.py list --color always | less -R
python main.py list --format tsv --show-ids | fzf
python main.py list --format jsonl | jq .
python main.py mark-read <number>
python main.py remove <number>
python main.py capacity 5
python main.py clear
```

`list` output includes a 1-based number column and a `status` field (`unread`/`read`) so you can distinguish entry state across output formats.
By default, links marked as read are hidden from `list`; use `--include-read` to display them.
Use `--color always` to force ANSI colors when piping table output (for example to `less -R`).

## Storage

By default, data is stored in `~/.bejw/links.json`.
