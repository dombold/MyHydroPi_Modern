from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.config import settings
from backend.dependencies import get_db
from backend.models.relay import TimerPair

router = APIRouter()


@router.get("/timers")
def get_timers(db: Connection = Depends(get_db)):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.get_timers()

    from backend.database import get_relay_columns, get_engine
    relay_cols = get_relay_columns(get_engine())

    result = {}
    for col in relay_cols:
        table = f"{col}_timer"
        rows = db.execute(text(f"SELECT * FROM `{table}` ORDER BY pk")).mappings().all()
        result[col] = [
            {
                "pk": r["pk"],
                "starttime": r["starttime"].strftime("%Y-%m-%d %H:%M:%S") if r["starttime"] else None,
                "stoptime": r["stoptime"].strftime("%Y-%m-%d %H:%M:%S") if r["stoptime"] else None,
            }
            for r in rows
        ]
    return result


@router.put("/timers/{relay_id}")
def update_timers(
    relay_id: str,
    pairs: list[TimerPair],
    db: Connection = Depends(get_db),
):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.update_timers(relay_id, pairs)

    # Validate relay_id
    from backend.database import get_relay_columns, get_engine
    valid = get_relay_columns(get_engine())
    if relay_id not in valid:
        raise HTTPException(status_code=404, detail="Unknown relay")

    table = f"{relay_id}_timer"
    for pair in pairs:
        db.execute(
            text(
                f"UPDATE `{table}` SET starttime = :start, stoptime = :stop WHERE pk = :pk"
            ),
            {"start": pair.starttime or None, "stop": pair.stoptime or None, "pk": pair.pk},
        )
    db.commit()
    return {"relay_id": relay_id, "updated": len(pairs)}
