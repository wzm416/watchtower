FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md ./
COPY watchtower_api ./watchtower_api/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "watchtower_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
