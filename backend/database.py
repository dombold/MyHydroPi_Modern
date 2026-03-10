from functools import lru_cache

from sqlalchemy import create_engine, pool, text
from sqlalchemy.engine import Engine

from backend.config import settings


def _build_url() -> str:
    return (
        f"mysql+mysqlconnector://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}/{settings.db_name}"
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(
        _build_url(),
        poolclass=pool.QueuePool,
        pool_size=3,
        max_overflow=1,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


def get_sensor_columns(engine: Engine) -> list[str]:
    """Return non-timestamp column names from the sensors table."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'sensors' "
                "AND COLUMN_NAME != 'timestamp' ORDER BY ORDINAL_POSITION"
            ),
            {"db": settings.db_name},
        )
        return [row[0] for row in result]


def get_relay_columns(engine: Engine) -> list[str]:
    """Return relay column names from timer_override (excludes pk)."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'timer_override' "
                "AND COLUMN_NAME != 'pk' ORDER BY ORDINAL_POSITION"
            ),
            {"db": settings.db_name},
        )
        return [row[0] for row in result]
