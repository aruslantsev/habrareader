# habrareader

Habrareader downloads Habr articles and comments into an async SQLite
database using SQLAlchemy.

## Features

- Async article and comment requests through `httpx`
- Shared request rate limiter and bounded concurrency
- Automatic retries for transport errors and HTTP 429/5xx responses
- SQLAlchemy 2 ORM persistence with `aiosqlite`
- Fresh database creation from ORM metadata
- CLI support for ranges, reverse processing, and failed downloads

## Requirements

- Python 3.11 or newer
- A virtual environment

## Installation

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Usage

Download a known article ID range:

```bash
.venv/bin/habrareader --start-id 1 --end-id 100
```

Continue after the highest article already represented in the database:

```bash
.venv/bin/habrareader
```

Download failed articles:

```bash
.venv/bin/habrareader --only-missing
```

Process IDs newest-to-oldest:

```bash
.venv/bin/habrareader --start-id 100 --end-id 200 --reverse
```

Control HTTP behavior:

```bash
.venv/bin/habrareader \
    --requests-per-second 5 \
    --concurrency 10
```

Available options:

- `--start-id`: first article ID
- `--end-id`: final article ID
- `--reverse`: process IDs newest-to-oldest
- `--only-missing`: process articles whose state is unsuccessful
- `--requests-per-second`: shared request rate, default `5`
- `--concurrency`: maximum concurrent HTTP requests, default `10`

## Database

The database is created automatically at `database.sqlite`. Existing data is
not migrated; remove the file to start with a fresh database:

```bash
rm -f database.sqlite
```

The SQLAlchemy metadata is canonical in
`habrareader/data/model.py`. Database setup is centralized in
`habrareader/data/database.py`.

## Architecture

- `habrareader/download/article.py` parses article responses and RSS data
  into ORM objects.
- `habrareader/download/comment.py` builds comment, author, content, and
  child-comment ORM graphs.
- `habrareader/download/client.py` owns the shared HTTP client, semaphore,
  retry policy, and rate limiter.
- `habrareader/download/database_helpers.py` merges downloaded ORM graphs
  and refreshes comments transactionally.
- `habrareader/download.py` schedules bounded concurrent downloads and
  serializes database writes.

## Development

Run tests:

```bash
.venv/bin/python -m pytest
```

Run Flake8:

```bash
.venv/bin/python -m flake8 habrareader tests
```

Tests use temporary or in-memory SQLite databases and mocked HTTP responses.
Live API requests are deliberately excluded from normal test runs.