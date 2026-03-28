# Watchtower API

FastAPI service for merchandise price monitoring.

## Setup

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Point `DATABASE_URL` at a local Postgres instance, then apply migrations:

```bash
export DATABASE_URL=postgresql://watchtower:watchtower@localhost:5432/watchtower
alembic upgrade head
```

## Run

```bash
uvicorn watchtower_api.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/health`
- OpenAPI: `http://localhost:8000/docs`

## Test

```bash
pytest
ruff check .
ruff format --check .
```

With `DATABASE_URL` set, `tests/test_db_smoke.py` runs against Postgres (same as CI). Without it, those tests are skipped.

## Docker

```bash
docker build -t watchtower-api .
docker run --rm -p 8000:8000 watchtower-api
```
