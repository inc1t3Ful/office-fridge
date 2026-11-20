# office-fridge

CLI tool for tracking what's in the office fridge — who put an item in and how long it's been there. Backed by a local SQLite database. No dependencies beyond the Python standard library.

## Requirements

Python 3.9+

## Usage

```
fridge.py <food> [owner] in [date]    Add an item to the fridge
fridge.py <food> [owner] out [date]   Remove an item from the fridge
fridge.py list                        Show current inventory
```

`[owner]` is optional. For `in`, it defaults to the `FRIDGE_DEFAULT_OWNER` environment variable, and is required if that is unset. For `out`, omitting it matches the food name across all owners.

```
export FRIDGE_DEFAULT_OWNER=sam
fridge.py milk in    # same as: fridge.py milk sam in
```

`[date]` is optional (format `YYYY-MM-DD`), defaults to today. For `in`, useful for backdating entries when first populating the db; future dates are rejected. For `out`, disambiguates when the same food/owner has multiple entries.

Food and owner names are lowercased before they are stored or matched.

Quote multi-word names:

```
fridge.py "leftover pasta" Anthony in
fridge.py "leftover pasta" Anthony in 2026-09-01
fridge.py "leftover pasta" Anthony out 2026-09-01
fridge.py "leftover pasta" in
fridge.py "leftover pasta" out
```

Removing an item looks up matches by food name (case-insensitive), plus owner and date if given. If more than one match remains, it lists them and asks which to remove.

## Example

```
$ ./fridge.py "leftover pasta" Anthony in
Added: leftover pasta (anthony) — logged in on 2026-09-23

$ ./fridge.py milk Sam in
Added: milk (sam) — logged in on 2026-09-23

$ ./fridge.py list
      ITEM       |   OWNER   |   DATE IN    |  TIME IN 
-----------------+-----------+--------------+----------
 leftover pasta  |  anthony  |  2026-09-23  |   today  
      milk       |    sam    |  2026-09-23  |   today  

$ ./fridge.py milk Sam out
Removed: milk (sam), was in since 2026-09-23.
```

## Architecture

Single-file script, `fridge.py`. No install step — run directly with Python.

- **Storage**: SQLite database, `fridge.db`, created automatically next to the script on first run. Gitignored, since it's local state, not source.
- **Schema**: one table, `fridge_items(id, item, owner, date_in)`. `date_in` is stored as an ISO date string; elapsed time ("3 days", "2 weeks") is computed on read, not stored.
- **Output**: `list_items()` sizes each column to its widest value (header or data) and centers every cell — no fixed-width truncation.
- **Commands**: `in`, `out`, and `list` map directly to `add_item()`, `remove_item()`, and `list_items()` in `fridge.py`. `main()` parses `sys.argv` and dispatches to one of the three — there's no argument-parsing library involved.
- **Conflict handling**: `remove_item()` matches on food, plus owner and date if given. Zero matches reports nothing found; one match removes it; multiple matches prompts interactively, oldest first (showing each owner when none was given).
