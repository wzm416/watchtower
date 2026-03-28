from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from watchtower_api.config import get_settings

_engine: Engine | None = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, class_=Session)


def reset_engine() -> None:
    """Dispose engine (e.g. between tests)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = get_settings().database_url
        if not url:
            msg = "DATABASE_URL is required for database access"
            raise RuntimeError(msg)
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal(bind=get_engine())
    try:
        yield db
    finally:
        db.close()
