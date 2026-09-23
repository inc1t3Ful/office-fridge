#!/usr/bin/env python3
"""
fridge.py — simple office fridge inventory tracker (SQLite-backed)

Usage:
    fridge.py <food> <owner> in [date]   Add an item to the fridge
    fridge.py <food> <owner> out         Remove an item from the fridge
    fridge.py list                       Show current inventory

[date] is optional, format YYYY-MM-DD. Defaults to today. Useful for
backdating entries when first populating the db.

Quote multi-word names, e.g.:
    fridge.py "leftover pasta" Anthony in
    fridge.py "leftover pasta" Anthony in 2026-09-01
"""

import sys
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "fridge.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fridge_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            owner TEXT NOT NULL,
            date_in TEXT NOT NULL
        )
        """
    )
    return conn


def format_elapsed(date_in_str):
    """Human-friendly elapsed time, computed on the fly: days -> weeks -> months."""
    date_in = date.fromisoformat(date_in_str)
    days = (date.today() - date_in).days

    if days < 1:
        return "today"
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''}"
    if days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    months = days // 30
    return f"{months} month{'s' if months != 1 else ''}"


def add_item(food, owner, date_in=None):
    if date_in is None:
        date_in = date.today().isoformat()
    else:
        try:
            date.fromisoformat(date_in)
        except ValueError:
            print(f"Invalid date '{date_in}'. Use format YYYY-MM-DD.")
            return

    conn = get_connection()
    conn.execute(
        "INSERT INTO fridge_items (item, owner, date_in) VALUES (?, ?, ?)",
        (food, owner, date_in),
    )
    conn.commit()
    conn.close()
    print(f"Added: {food} ({owner}) — logged in on {date_in}")


def remove_item(food, owner):
    conn = get_connection()
    cur = conn.execute(
        "SELECT id, item, owner, date_in FROM fridge_items "
        "WHERE item = ? COLLATE NOCASE AND owner = ? COLLATE NOCASE "
        "ORDER BY date_in ASC",
        (food, owner),
    )
    matches = cur.fetchall()

    if not matches:
        print(f"No match found for '{food}' belonging to '{owner}'.")
        conn.close()
        return

    if len(matches) == 1:
        chosen = matches[0]
    else:
        print(f"Multiple matches found for '{food}' ({owner}):")
        for idx, (row_id, item, owner_name, date_in) in enumerate(matches, start=1):
            print(f"  [{idx}] in since {date_in} ({format_elapsed(date_in)} ago)")
        choice = input(f"Which one to remove? [1-{len(matches)}, or 'c' to cancel]: ").strip()
        if choice.lower() == "c":
            print("Cancelled.")
            conn.close()
            return
        try:
            chosen = matches[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid selection. Nothing removed.")
            conn.close()
            return

    row_id = chosen[0]
    conn.execute("DELETE FROM fridge_items WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()
    print(f"Removed: {food} ({owner}), was in since {chosen[3]}.")


def list_items():
    conn = get_connection()
    cur = conn.execute(
        "SELECT item, owner, date_in FROM fridge_items ORDER BY date_in ASC"
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Fridge is empty.")
        return

    headers = ("ITEM", "OWNER", "DATE IN", "TIME IN")
    table = [(item, owner, date_in, format_elapsed(date_in)) for item, owner, date_in in rows]

    widths = [
        max(len(header), *(len(row[i]) for row in table)) + 2
        for i, header in enumerate(headers)
    ]
    separator = "-+-".join("-" * w for w in widths)

    def format_row(cols):
        return " | ".join(col.center(w) for col, w in zip(cols, widths))

    print(format_row(headers))
    print(separator)
    for row in table:
        print(format_row(row))


def main():
    args = sys.argv[1:]

    if len(args) == 1 and args[0] == "list":
        list_items()
    elif len(args) in (3, 4) and args[2] == "in":
        food, owner = args[0], args[1]
        date_in = args[3] if len(args) == 4 else None
        add_item(food, owner, date_in)
    elif len(args) == 3 and args[2] == "out":
        food, owner, _ = args
        remove_item(food, owner)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()