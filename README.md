# Coffee Dependency Tracker

Log coffee consumption and get a tiny productivity forecast.

## Quick start

- `python main.py add --cups 1`
- `python main.py add --cups 2 --note "launch prep"`
- `python main.py stats`
- `python main.py stats --daily --days 14`
- `python main.py list --limit 5`
- `python main.py export --out coffee_log.csv`

Data is stored in `coffee_log.json` in the repo by default (or pass `--data` with a custom
`.json` or `.csv` path).

## Commands

- `add` — Log a coffee (`--at`, `--source`, `--note` supported)
- `stats` — Summary stats (`--since`, `--until`, `--daily`)
- `list` — Show recent entries (`--limit`)
- `export` — Export filtered data to JSON or CSV
- `import` — Replace the current log from a JSON or CSV file
