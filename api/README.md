# Watchtower API

FastAPI service for merchandise price monitoring.

## Setup

```bash
cd api
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
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

## Docker

```bash
docker build -t watchtower-api .
docker run --rm -p 8000:8000 watchtower-api
```
