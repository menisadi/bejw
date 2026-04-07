<div align="center">

# bejw

`A capped reading list in your terminal.`

</div>

## Install

```bash
uv tool install bejw
```

Or with pip:

```bash
pip install bejw
```

## Quick start

```bash
bejw init                # create a reading list (default capacity: 10)
bejw add URL TITLE       # save a link
bejw list                # show unread links
```

## Commands

```bash
bejw init [--capacity N]       # initialize the reading list
bejw add URL TITLE             # add a link (prompts to replace one if full)
bejw list                      # display unread links
bejw list --include-read       # include read links
bejw list --format tsv|csv|jsonl  # alternate output formats
bejw list --color always       # force colors (useful when piping to less -R)
bejw read N                    # open link #N in the browser
bejw mark-read N               # mark link #N as read
bejw remove N                  # remove link #N
bejw capacity                  # show current capacity
bejw capacity N                # set capacity to N
bejw clear                     # remove all links
```

## Storage

Data is stored in `~/.bejw/links.json` by default. All commands accept `--file-path` to use a different location.
