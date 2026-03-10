"""Simulated data returned when USE_MOCK=true (for development / testing)."""

import random
from datetime import datetime, timedelta

from backend.models.relay import MetaResponse, RelayMeta, RelayState, RelayStatesResponse, TimerPair
from backend.models.sensor import (
    SensorCurrentResponse,
    SensorHistoryPoint,
    SensorHistoryResponse,
    SensorMeta,
    SensorReading,
)
from backend.models.settings import SettingsResponse

# ── Static meta ───────────────────────────────────────────────────────────────

MOCK_META = MetaResponse(
    sensors=[
        SensorMeta(column="ds18b20_temp", display_name="Air Temp", unit="°C"),
        SensorMeta(column="atlas_temp", display_name="Pool Temp", unit="°C"),
        SensorMeta(column="ec", display_name="Salinity", unit="ppm"),
        SensorMeta(column="ph", display_name="pH", unit=""),
        SensorMeta(column="orp", display_name="ORP", unit="mV"),
    ],
    relays=[
        RelayMeta(id="relay_1", display_name="Main Pump", table="relay_1_timer", dt_pairs=4),
        RelayMeta(id="relay_2", display_name="Filter", table="relay_2_timer", dt_pairs=3),
        RelayMeta(id="relay_3", display_name="Lights", table="relay_3_timer", dt_pairs=2),
        RelayMeta(id="relay_4", display_name="Spare", table="relay_4_timer", dt_pairs=1),
    ],
)

# ── In-memory relay state store (mutated by PUT /api/relays/{id}/state) ──────

_relay_overrides: dict[str, str] = {
    "relay_1": "auto",
    "relay_2": "off",
    "relay_3": "on",
    "relay_4": "auto",
}

_relay_is_on: dict[str, bool] = {
    "relay_1": True,
    "relay_2": False,
    "relay_3": True,
    "relay_4": False,
}

# ── In-memory timer store ─────────────────────────────────────────────────────

_timers: dict[str, list[dict]] = {
    "relay_1": [
        {"pk": 1, "starttime": "2026-03-10 08:00:00", "stoptime": "2026-03-10 20:00:00"},
        {"pk": 2, "starttime": None, "stoptime": None},
        {"pk": 3, "starttime": None, "stoptime": None},
        {"pk": 4, "starttime": None, "stoptime": None},
    ],
    "relay_2": [
        {"pk": 1, "starttime": "2026-03-10 06:00:00", "stoptime": "2026-03-10 09:00:00"},
        {"pk": 2, "starttime": "2026-03-10 18:00:00", "stoptime": "2026-03-10 21:00:00"},
        {"pk": 3, "starttime": None, "stoptime": None},
    ],
    "relay_3": [
        {"pk": 1, "starttime": "2026-03-10 19:00:00", "stoptime": "2026-03-10 23:00:00"},
        {"pk": 2, "starttime": None, "stoptime": None},
    ],
    "relay_4": [
        {"pk": 1, "starttime": None, "stoptime": None},
    ],
}

# ── In-memory settings store ──────────────────────────────────────────────────

_settings: dict = {
    "ds18b20_temp_hi": 50.0,
    "ds18b20_temp_low": 10.0,
    "atlas_temp_hi": 40.0,
    "atlas_temp_low": 25.0,
    "ec_hi": 6000.0,
    "ec_low": 4500.0,
    "ph_hi": 7.4,
    "ph_low": 7.0,
    "orp_hi": 700.0,
    "orp_low": 550.0,
    "read_sensor_delay": 300,
    "email_reset_delay": 172800,
    "pause_reset_delay": 1800,
    "pause_readings": False,
    "to_email": "user@example.com",
    "pool_size": 27000,
}

_pause_active = False


# ── Public helpers ─────────────────────────────────────────────────────────────


def get_meta() -> MetaResponse:
    return MOCK_META


def get_sensor_current() -> SensorCurrentResponse:
    readings = [
        SensorReading(
            name="ds18b20_temp", display_name="Air Temp",
            value=round(22.5 + random.uniform(-0.5, 0.5), 1),
            avg_24h=21.3, unit="°C",
            alert_high=50.0, alert_low=10.0, in_alert=False,
        ),
        SensorReading(
            name="atlas_temp", display_name="Pool Temp",
            value=round(28.3 + random.uniform(-0.3, 0.3), 1),
            avg_24h=27.8, unit="°C",
            alert_high=40.0, alert_low=25.0, in_alert=False,
        ),
        SensorReading(
            name="ec", display_name="Salinity",
            value=round(4800 + random.uniform(-50, 50)),
            avg_24h=4750.0, unit="ppm",
            alert_high=6000.0, alert_low=4500.0, in_alert=False,
        ),
        SensorReading(
            name="ph", display_name="pH",
            value=round(7.2 + random.uniform(-0.05, 0.05), 2),
            avg_24h=7.18, unit="",
            alert_high=7.4, alert_low=7.0, in_alert=False,
        ),
        SensorReading(
            name="orp", display_name="ORP",
            value=round(620 + random.uniform(-10, 10)),
            avg_24h=615.0, unit="mV",
            alert_high=700.0, alert_low=550.0, in_alert=False,
        ),
    ]
    return SensorCurrentResponse(
        readings=readings,
        timestamp=datetime.now(),
        pause_active=_pause_active,
    )


def get_relay_states() -> RelayStatesResponse:
    relays = []
    for relay_meta in MOCK_META.relays:
        relays.append(RelayState(
            id=relay_meta.id,
            display_name=relay_meta.display_name,
            override=_relay_overrides[relay_meta.id],
            is_on=_relay_is_on[relay_meta.id],
        ))
    return RelayStatesResponse(relays=relays)


def update_relay_state(relay_id: str, state: str) -> dict:
    _relay_overrides[relay_id] = state
    if state == "on":
        _relay_is_on[relay_id] = True
    elif state == "off":
        _relay_is_on[relay_id] = False
    # "auto" — leave is_on as-is (would be set by timer in real system)
    return {"relay_id": relay_id, "state": state}


def get_timers() -> dict[str, list[TimerPair]]:
    result = {}
    for relay_id, pairs in _timers.items():
        result[relay_id] = [TimerPair(**p) for p in pairs]
    return result


def update_timers(relay_id: str, pairs: list[TimerPair]) -> dict:
    _timers[relay_id] = [p.model_dump() for p in pairs]
    return {"relay_id": relay_id, "updated": len(pairs)}


def get_settings() -> SettingsResponse:
    return SettingsResponse(**_settings)


def update_settings(data: dict) -> dict:
    _settings.update(data)
    return {"updated": True}


def pause_sensors() -> dict:
    global _pause_active
    _pause_active = True
    return {"paused": True}


def delete_sensor_history(older_than_days: int) -> dict:
    # Mock: pretend we deleted some rows
    deleted = max(0, 300 - older_than_days * 5)
    return {"deleted": deleted}


def get_sensor_history(sensor: str, days: int) -> SensorHistoryResponse:
    """Generate realistic mock time-series for a sensor over `days` days."""
    _defaults = {
        "ds18b20_temp": (22.5, 1.5),
        "atlas_temp": (28.3, 0.8),
        "ec": (4800, 100),
        "ph": (7.2, 0.08),
        "orp": (620, 15),
    }
    base, spread = _defaults.get(sensor, (50, 5))
    points_per_day = 12  # one per 2 hours
    total_points = days * points_per_day
    interval = timedelta(hours=2)
    start = datetime.now() - timedelta(days=days)

    data = []
    val = base
    for i in range(total_points):
        val = round(val + random.uniform(-spread * 0.3, spread * 0.3), 2)
        # Clamp within ±spread of base
        val = max(base - spread, min(base + spread, val))
        dt = start + interval * i
        label = dt.strftime("%d/%m %H:%M")
        data.append(SensorHistoryPoint(label=label, value=val))

    return SensorHistoryResponse(sensor=sensor, data=data)
