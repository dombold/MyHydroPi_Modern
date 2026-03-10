from pydantic import BaseModel


class SettingsResponse(BaseModel):
    # Sensor alert thresholds (dynamic - generated from sensor config)
    ds18b20_temp_hi: float | None = None
    ds18b20_temp_low: float | None = None
    atlas_temp_hi: float | None = None
    atlas_temp_low: float | None = None
    ec_hi: float | None = None
    ec_low: float | None = None
    ph_hi: float | None = None
    ph_low: float | None = None
    orp_hi: float | None = None
    orp_low: float | None = None

    # System settings
    read_sensor_delay: int | None = None
    email_reset_delay: int | None = None
    pause_reset_delay: int | None = None
    pause_readings: bool | None = None
    to_email: str | None = None
    pool_size: int | None = None

    model_config = {"extra": "allow"}


class SettingsUpdate(BaseModel):
    model_config = {"extra": "allow"}
