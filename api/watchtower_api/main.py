from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from watchtower_api.config import get_settings
from watchtower_api.routers import health

settings = get_settings()

app = FastAPI(
    title="Watchtower API",
    version="0.1.0",
    description="Merchandise price monitoring backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "watchtower-api", "docs": "/docs"}
