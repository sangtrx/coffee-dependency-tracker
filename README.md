# Coffee Dependency Tracker

Log coffee consumption and get a tiny productivity forecast.

## Quick start

- `python -m pip install -e .`
- `coffee-dependency-tracker --help`
- `python main.py add --cups 1`
- `python main.py add --cups 2 --note "launch prep"`
- `python main.py stats`
- `python main.py stats --daily --days 14`
- `python -m coffee_dependency_tracker --help`
- `python main.py report --days 14`
- `python main.py list --limit 5`
- `python main.py export --out coffee_log.csv`
- `python main.py export --out coffee_log.csv --force`

Data is stored in `coffee_log.json` in the repo by default (or pass `--data` with a custom
`.json` or `.csv` path).

Import behavior: the `import` command accepts JSON or CSV files and replaces the current
log with the imported data. Importing a non-existent or malformed file will result in an
empty log (the command reports "Imported 0 entries").

## Commands

- `add` — Log a coffee (`--at`, `--source`, `--note` supported)
- `stats` — Summary stats (`--since`, `--until`, `--daily`)
- `report` — Detailed report with trend, streaks, and sparkline (`--since`, `--until`, `--days`, `--no-chart`)
- `list` — Show recent entries (`--limit`)
- `export` — Export filtered data to JSON or CSV (`--force` overwrites an existing file)
- `import` — Replace the current log from a JSON or CSV file

Validation:

- `--cups` must be greater than 0
- `--at` cannot be in the future
