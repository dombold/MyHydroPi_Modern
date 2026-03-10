from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.config import settings
from backend.dependencies import get_db
from backend.models.relay import MetaResponse, RelayMeta
from backend.models.sensor import SensorMeta

router = APIRouter()

# Display name mapping (column → human label + unit)
_SENSOR_DISPLAY: dict[str, tuple[str, str]] = {
    "ds18b20_temp": ("Air Temp", "°C"),
    "atlas_temp":   ("Pool Temp", "°C"),
    "ec":           ("Salinity", "ppm"),
    "ph":           ("pH", ""),
    "orp":          ("ORP", "mV"),
}

_RELAY_DISPLAY: dict[str, str] = {
    "relay_1": "Main Pump",
    "relay_2": "Filter",
    "relay_3": "Lights",
    "relay_4": "Spare",
}


@lru_cache(maxsize=1)
def _cached_meta_db() -> MetaResponse:
    """Builds meta from live DB — cached until process restarts."""
    from backend.database import get_engine, get_relay_columns, get_sensor_columns

    engine = get_engine()
    sensor_cols = get_sensor_columns(engine)
    relay_cols = get_relay_columns(engine)

    sensors = [
        SensorMeta(
            column=col,
            display_name=_SENSOR_DISPLAY.get(col, (col, ""))[0],
            unit=_SENSOR_DISPLAY.get(col, ("", ""))[1],
        )
        for col in sensor_cols
    ]

    # Determine dt_pairs per relay from DB
    with engine.connect() as conn:
        relays = []
        for col in relay_cols:
            table = f"{col}_timer"
            row = conn.execute(
                text("SELECT COUNT(*) FROM :tbl"),
                {"tbl": table},
            ).scalar()
            relays.append(RelayMeta(
                id=col,
                display_name=_RELAY_DISPLAY.get(col, col),
                table=table,
                dt_pairs=row or 1,
            ))

    return MetaResponse(sensors=sensors, relays=relays)


@router.get("/meta", response_model=MetaResponse)
def get_meta():
    if settings.use_mock:
        from backend import mock_data
        return mock_data.get_meta()
    return _cached_meta_db()
