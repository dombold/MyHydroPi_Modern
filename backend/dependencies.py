from collections.abc import Generator

from backend.config import settings


def get_db() -> Generator:
    """
    Yields a database connection when USE_MOCK=False.
    Yields None in mock mode — routers check settings.use_mock before using db.
    """
    if settings.use_mock:
        yield None
        return

    from sqlalchemy.engine import Connection
    from backend.database import get_engine

    engine = get_engine()
    with engine.connect() as conn:
        yield conn
