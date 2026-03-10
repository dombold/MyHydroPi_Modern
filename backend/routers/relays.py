from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.config import settings
from backend.dependencies import get_db
from backend.models.relay import RelayState, RelayStatesResponse, RelayStateUpdate

router = APIRouter()

_VALID_STATES = {"on", "off", "auto"}
_RELAY_DISPLAY = {
    "relay_1": "Main Pump",
    "relay_2": "Filter",
    "relay_3": "Lights",
    "relay_4": "Spare",
}


@router.get("/relays/states", response_model=RelayStatesResponse)
def get_relay_states(db: Connection = Depends(get_db)):
    if settings.use_mock:
        from backend import mock_data
        return mock_data.get_relay_states()

    from backend.database import get_relay_columns, get_engine
    relay_cols = get_relay_columns(get_engine())

    override_row = db.execute(
        text("SELECT * FROM timer_override WHERE pk = 1")
    ).mappings().first()
    state_row = db.execute(
        text("SELECT * FROM timer_override WHERE pk = 2")
    ).mappings().first()

    relays = []
    for col in relay_cols:
        override = override_row[col] if override_row else "off"
        raw_state = state_row[col] if state_row else "False"
        is_on = str(raw_state).lower() in ("true", "1")
        relays.append(RelayState(
            id=col,
            display_name=_RELAY_DISPLAY.get(col, col),
            override=override,
            is_on=is_on,
        ))

    return RelayStatesResponse(relays=relays)


@router.put("/relays/{relay_id}/state")
def update_relay_state(
    relay_id: str,
    body: RelayStateUpdate,
    db: Connection = Depends(get_db),
):
    if body.state not in _VALID_STATES:
        raise HTTPException(status_code=422, detail=f"state must be one of {_VALID_STATES}")

    if settings.use_mock:
        from backend import mock_data
        return mock_data.update_relay_state(relay_id, body.state)

    # Validate relay_id against live schema
    from backend.database import get_relay_columns, get_engine
    valid = get_relay_columns(get_engine())
    if relay_id not in valid:
        raise HTTPException(status_code=404, detail="Unknown relay")

    db.execute(
        text(f"UPDATE timer_override SET `{relay_id}` = :state WHERE pk = 1"),
        {"state": body.state},
    )
    db.commit()
    return {"relay_id": relay_id, "state": body.state}


@router.get("/relays/gpio")
def get_gpio_states(db: Connection = Depends(get_db)):
    """Returns the physical on/off state of each relay (pk=2 in timer_override)."""
    if settings.use_mock:
        from backend import mock_data
        states = mock_data.get_relay_states()
        return {r.id: r.is_on for r in states.relays}

    from backend.database import get_relay_columns, get_engine
    relay_cols = get_relay_columns(get_engine())
    state_row = db.execute(
        text("SELECT * FROM timer_override WHERE pk = 2")
    ).mappings().first()

    return {
        col: str(state_row[col]).lower() in ("true", "1")
        for col in relay_cols
    }
