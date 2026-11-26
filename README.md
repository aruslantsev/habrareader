# habrareader

A data downloader for Habr articles and comments.

## Setup

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Usage

```bash
.venv/bin/habrareader --start-id 1 --end-id 100
.venv/bin/habrareader --only-missing
.venv/bin/habrareader --reverse --start-id 100 --end-id 200
```

Available options:

- `--start-id`: first article ID to download
- `--end-id`: final article ID to download
- `--reverse`: process IDs newest-to-oldest
- `--only-missing`: process IDs marked as failed
- `--requests-per-second`: shared HTTP request rate limit, default `5`
- `--concurrency`: maximum concurrent HTTP requests, default `10`

## Database

The application uses SQLAlchemy 2 and an async SQLite driver. The database is created automatically at `database.sqlite`. Legacy databases are not migrated and can be deleted safely before a fresh download:

```bash
rm -f database.sqlite
```

SQLite writes are serialized per article after bounded concurrent HTTP fetching. HTTP requests share one rate limiter and semaphore.

## Tests

```bash
.venv/bin/python -m pytest
```