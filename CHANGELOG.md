# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

## [0.7.0] - 2026-11-10

- Added `--version` / `-V` to print the installed version.

## [0.6.1] - 2026-11-09

- `mark-read` now prints the title of the link it marked (e.g.
  "Marked #2 as read: Example Two"), so you can confirm it hit the right one.

## [0.6.0] - 2026-08-19

- `init` now reports what an existing reading list holds and asks before
  discarding it, instead of overwriting silently. Added `init --force` to skip
  the prompt in scripts.

## [0.5.0] - 2026-08-19

- `capacity N` now refuses to raise the capacity while the list is full; mark a
  link as read first. Lowering is still always allowed, and raising with
  headroom is unchanged.
- `capacity` now reports the last capacity change on stderr (e.g.
  "(raised from 10, 3 days ago)"), keeping the bare number on stdout for pipes.
- `capacity` rejects values below 1, which would otherwise lock out any future
  raise.

## [0.4.1] - 2026-03-22

- Show capacity in list table title (e.g. "12/15")
- Capacity now only counts unread links, so marking a link as read frees a slot
- `capacity` command without arguments now shows the current capacity

## [0.4.0] - 2026-03-22

- Interactive replace: when adding a link to a full list, pick an existing link to replace instead of failing.

## [0.3.3] - 2026-02-16

- Fix: numbering on all command now use the same numbering (counting only unread links)

## [0.3.2] - 2026-02-16

- Added `list --color auto|always|never` to control ANSI color output (useful for pipes like `less -R`).

## [0.3.1] - 2026-02-16

- Added 'status' on 'list' output (read/unread)

## [0.3.0] - 2026-02-16

- mark-read command
- persisted read_at
- list now hides read links by default
- --include-read flag

## [0.2.4] - 2026-02-16

- Add `read` command to open links by numbered entry.

## [0.2.3] - 2026-02-12

- Enumerating the list (by date added)
- Use the numbered entries for removal

## [0.2.2] - 2026-02-11

- Simpler table format

## [0.2.1] - 2026-02-11

- Fixing entry point

## [0.2.0] - 2026-02-11

- Fixed project structure.
- UI improvements.

## [0.1.0] - 2026-02-11

- Initial pre-release.
