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
python main.py list --format tsv --show-ids | fzf
python main.py list --format jsonl | jq .
python main.py remove <id>
python main.py capacity 5
python main.py clear
```

## Storage

By default, data is stored in `~/.bejw/links.json`.
