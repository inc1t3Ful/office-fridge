# office-fridge

CLI tool for tracking what's in the office fridge — who put an item in and how long it's been there. Backed by a local SQLite database. No dependencies beyond the Python standard library.

## Requirements

Python 3.9+

## Usage

```
fridge.py <food> <owner> in      Add an item to the fridge
fridge.py <food> <owner> out     Remove an item from the fridge
fridge.py list                   Show current inventory
```

Quote multi-word names:

```
fridge.py "leftover pasta" Anthony in
```

Removing an item looks up matches by food name and owner (case-insensitive). If more than one match exists, it lists them and asks which to remove.

## Example

```
$ ./fridge.py "leftover pasta" Anthony in
Added: leftover pasta (Anthony) — logged in on 2026-09-23

$ ./fridge.py milk Sam in
Added: milk (Sam) — logged in on 2026-09-23

$ ./fridge.py list
ITEM                   OWNER           DATE IN      TIME IN
-----------------------------------------------------------------
leftover pasta         Anthony         2026-09-23   today
milk                   Sam             2026-09-23   today

$ ./fridge.py milk Sam out
Removed: milk (Sam), was in since 2026-09-23.
```

## Architecture

Single-file script, `fridge.py`. No install step — run directly with Python.

- **Storage**: SQLite database, `fridge.db`, created automatically next to the script on first run. Gitignored, since it's local state, not source.
- **Schema**: one table, `fridge_items(id, item, owner, date_in)`. `date_in` is stored as an ISO date string; elapsed time ("3 days", "2 weeks") is computed on read, not stored.
- **Commands**: `in`, `out`, and `list` map directly to `add_item()`, `remove_item()`, and `list_items()` in `fridge.py`. `main()` parses `sys.argv` and dispatches to one of the three — there's no argument-parsing library involved.
- **Conflict handling**: `remove_item()` matches on food + owner. Zero matches reports nothing found; one match removes it; multiple matches prompts interactively, oldest first.
