from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.config import settings
from backend.dependencies import get_db
from backend.models.settings import SettingsResponse, SettingsUpdate

router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
def get_settings(db: Connection = Depends(get_db)):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.get_settings()

    row = db.execute(
        text("SELECT * FROM settings WHERE pk = 1")
    ).mappings().first()

    if row is None:
        return SettingsResponse()

    data = dict(row)
    data.pop("pk", None)
    if data.get("offset_percent") is not None:
        data["offset_percent"] = float(data["offset_percent"])
    return SettingsResponse(**data)


@router.put("/settings")
def update_settings(body: SettingsUpdate, db: Connection = Depends(get_db)):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.update_settings(body.model_dump(exclude_none=True))

    data = body.model_dump(exclude_none=True)
    if not data:
        return {"updated": False}

    # Build SET clause — column names come from our model, not user input
    # Use a whitelist of known safe column names derived from the model fields
    allowed = set(SettingsResponse.model_fields.keys())
    safe_data = {k: v for k, v in data.items() if k in allowed}

    set_clause = ", ".join(f"`{k}` = :{k}" for k in safe_data)
    db.execute(
        text(f"UPDATE settings SET {set_clause} WHERE pk = 1"),
        safe_data,
    )
    db.commit()
    return {"updated": True}
