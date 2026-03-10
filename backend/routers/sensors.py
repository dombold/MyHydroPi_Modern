from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.config import settings
from backend.dependencies import get_db
from backend.models.sensor import SensorCurrentResponse, SensorHistoryResponse

router = APIRouter()


@router.get("/sensors/current", response_model=SensorCurrentResponse)
def get_current(db: Connection = Depends(get_db)):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.get_sensor_current()

    # Live: fetch latest row + 24h averages
    row = db.execute(
        text("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT 1")
    ).mappings().first()

    avgs_row = db.execute(
        text(
            "SELECT * FROM sensors WHERE timestamp >= :since "
            "ORDER BY timestamp DESC"
        ),
        {"since": datetime.now() - timedelta(hours=24)},
    ).mappings().all()

    settings_row = db.execute(
        text("SELECT * FROM settings WHERE pk = 1")
    ).mappings().first()

    from backend.database import get_sensor_columns, get_engine
    sensor_cols = get_sensor_columns(get_engine())

    readings = []
    for col in sensor_cols:
        vals = [r[col] for r in avgs_row if r[col] is not None]
        avg = round(sum(vals) / len(vals), 2) if vals else None
        value = float(row[col]) if row and row[col] is not None else None
        hi = float(settings_row[f"{col}_hi"]) if settings_row and f"{col}_hi" in settings_row else None
        lo = float(settings_row[f"{col}_low"]) if settings_row and f"{col}_low" in settings_row else None
        in_alert = False
        if value is not None:
            if hi is not None and value > hi:
                in_alert = True
            if lo is not None and value < lo:
                in_alert = True

        from backend.routers.meta import _SENSOR_DISPLAY
        readings.append({
            "name": col,
            "display_name": _SENSOR_DISPLAY.get(col, (col, ""))[0],
            "value": value,
            "avg_24h": avg,
            "unit": _SENSOR_DISPLAY.get(col, ("", ""))[1],
            "alert_high": hi,
            "alert_low": lo,
            "in_alert": in_alert,
        })

    pause = bool(settings_row["pause_readings"]) if settings_row else False
    ts = row["timestamp"] if row else None
    return SensorCurrentResponse(readings=readings, timestamp=ts, pause_active=pause)


@router.get("/sensors/history", response_model=SensorHistoryResponse)
def get_history(
    sensor: str = Query(...),
    days: int = Query(1, ge=1, le=365),
    db: Connection = Depends(get_db),
):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.get_sensor_history(sensor, days)

    # Whitelist sensor column
    from backend.database import get_sensor_columns, get_engine
    valid = get_sensor_columns(get_engine())
    if sensor not in valid:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Unknown sensor")

    since = datetime.now() - timedelta(days=days)
    rows = db.execute(
        text(f"SELECT timestamp, `{sensor}` FROM sensors WHERE timestamp >= :since ORDER BY timestamp"),
        {"since": since},
    ).all()

    data = [
        {"label": r[0].strftime("%d/%m %H:%M"), "value": float(r[1]) if r[1] is not None else None}
        for r in rows
    ]
    return SensorHistoryResponse(sensor=sensor, data=data)


@router.post("/sensors/pause")
def pause_sensors(db: Connection = Depends(get_db)):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.pause_sensors()

    db.execute(text("UPDATE settings SET pause_readings = 1 WHERE pk = 1"))
    db.commit()
    return {"paused": True}


@router.delete("/sensors/history")
def delete_history(
    older_than_days: int = Query(30, ge=0),
    db: Connection = Depends(get_db),
):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.delete_sensor_history(older_than_days)

    if older_than_days == 0:
        result = db.execute(text("DELETE FROM sensors"))
    else:
        cutoff = datetime.now() - timedelta(days=older_than_days)
        result = db.execute(
            text("DELETE FROM sensors WHERE timestamp < :cutoff"),
            {"cutoff": cutoff},
        )
    db.commit()
    return {"deleted": result.rowcount}
