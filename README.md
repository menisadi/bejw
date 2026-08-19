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
bejw capacity N                # set capacity to N (see Capacity below)
bejw clear                     # remove all links
```

## Capacity

The cap is the point of the tool, so raising it has one rule: **you cannot raise
capacity while the list is full.** Mark something read first.

```bash
$ bejw capacity 15
Reading list is full. Mark something read before raising capacity.
```

Lowering is always allowed, and raising works normally whenever there is
headroom — so deciding "10 was the wrong number for me" costs nothing. What the
rule blocks is the reflexive raise: hitting a full list mid-flow and moving the
cap instead of reading something.

Every change is recorded, and `bejw capacity` reports the last one on stderr so
drift stays visible while the bare number stays pipe-friendly:

```bash
$ bejw capacity
15
(raised from 10, 3 days ago)
```

## Storage

Data is stored in `~/.bejw/links.json` by default. All commands accept `--file-path` to use a different location.
