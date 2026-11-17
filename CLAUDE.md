# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CLI that tracks what's in the office fridge: who put each item in and since when. It is a single script, `fridge.py`, targeting Python 3.9+ with only the standard library and no install step. `README.md` has usage examples.

## Commands

There is no test suite, linter, formatter, or build step.

```sh
python3 fridge.py list
python3 fridge.py "leftover pasta" Anthony in [YYYY-MM-DD]
python3 fridge.py "leftover pasta" Anthony out [YYYY-MM-DD]
```

To try a change, run a copy. The database path comes from the script's location, so running `fridge.py` in place reads and writes the real `fridge.db`, which is gitignored and can hold live inventory data.

```sh
d=$(mktemp -d) && cp fridge.py "$d" && python3 "$d/fridge.py" list
```

## Architecture

- `main()` dispatches on positional `sys.argv` (no argparse) to `add_item()`, `remove_item()`, or `list_items()`. The verb is `args[2]` for `in`/`out`, or `args[1]` when the owner is omitted on `in` (which then uses `DEFAULT_OWNER`); `list` is the only argument on its own.
- `get_connection()` runs `CREATE TABLE IF NOT EXISTS` on every call. That is the only schema management, so changing `fridge_items` columns will not reach an existing `fridge.db` without a migration you write.
- Elapsed time is computed on read by `format_elapsed()` and never stored.

## Behavior to account for

- The module docstring is the CLI's usage output (`main()` prints `__doc__`). When the CLI changes, update it along with the README's Usage and Architecture sections.
- `date_in` is TEXT, and the code relies on it being canonical `YYYY-MM-DD`: `out` compares dates as strings, and `list` and `out` sort them lexically. Validate date input with `is_valid_date()`, because `date.fromisoformat` alone accepts other forms on Python 3.11+.
- Handled failures (invalid date, no match, bad selection) print a message and exit 0. Only usage errors exit 1, so check output rather than exit codes.
- `out` prompts through `input()` when several rows match, which raises `EOFError` if stdin is closed. Pipe a choice in when running non-interactively: `echo 1 | python3 fridge.py milk Sam out`.
- When testing any changes or working on this repo, DO NOT delete or modify the `fridge.db` if it exists. The db is live and must remain intact.